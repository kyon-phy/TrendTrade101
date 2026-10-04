"""Unlevered delayed-order ledger, used only with an explicit execution policy."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from math import floor, isfinite

@dataclass(frozen=True)
class LedgerPolicy:
    cap_basis: str
    shrink_only: bool
    tax_timing: str
    cross_year_loss_carry: bool

    def __post_init__(self):
        if self.cap_basis != "market_value" or self.tax_timing != "realization_accrual" or self.cross_year_loss_carry:
            raise ValueError("Requested ledger convention is not implemented")

@dataclass
class Position:
    quantity: int = 0
    cost: float = 0
    gross_cost: float = 0
    first_fill: datetime | None = None

    @property
    def average_cost(self) -> float | None:
        """Fee-inclusive cost per currently held historical share."""
        return self.cost/self.quantity if self.quantity else None

@dataclass
class Order:
    event_id: str
    ticker: str
    side: str
    signal_time: datetime
    due_time: datetime
    slope: float
    adx: float | None
    target: float
    quantity: int
    reservation: float
    reason: str
    status: str = "queued"
    cap_reservation: float = 0

class Ledger:
    def __init__(self, *, capital: float, position_cap: float, fee_rate: float,
                 fee_cap: float, tax_rate: float, lots: dict[str,int], policy: LedgerPolicy):
        if capital <= 0 or position_cap <= 0 or not 0 <= tax_rate < 1:
            raise ValueError("Invalid account")
        if any(not isinstance(v,int) or v <= 0 for v in lots.values()):
            raise ValueError("Verified positive lot sizes are required")
        self.initial_capital = self.cash = capital
        self.cap, self.fee_rate, self.fee_cap, self.tax_rate = position_cap, fee_rate, fee_cap, tax_rate
        self.lots, self.policy = lots, policy
        self.positions, self.marks = {}, {}
        self.orders, self.events, self.trades = [], [], []
        self.ids = set()
        self.realized, self.tax_paid = {}, {}
        self.fees = self.taxes = 0.0

    def fee(self, amount):
        return min(amount*self.fee_rate, self.fee_cap)

    @property
    def reserved(self):
        return sum(o.reservation for o in self.orders if o.status == "queued")

    @property
    def reserved_notional(self):
        return sum(o.cap_reservation for o in self.orders if o.status == "queued")

    @property
    def exposure(self):
        return sum(p.quantity*self.marks[t] for t,p in self.positions.items() if p.quantity)

    @property
    def equity(self):
        return self.cash + self.exposure

    def mark(self, ticker, price):
        if not isfinite(price) or price <= 0:
            raise ValueError("Invalid mark")
        self.marks[ticker] = price

    def apply_split(self, ticker: str, ratio: float, at: datetime):
        if not isfinite(ratio) or ratio <= 0:
            raise ValueError("Invalid split ratio")
        position = self.positions.get(ticker)
        quantity_before=position.quantity if position else 0
        held=position.quantity*ratio if position else 0
        if abs(held-round(held))>1e-8:
            raise ValueError("Fractional split entitlements require an audited cash-in-lieu model")
        if round(held)%self.lots[ticker]:
            raise ValueError("Split-created odd-lot holdings require an audited execution model")
        if position:
            position.quantity=int(round(held))
        for order in self.orders:
            if order.ticker==ticker and order.side=="buy" and order.status=="queued":
                before=order.quantity
                order.quantity=floor((before*ratio+1e-9)/self.lots[ticker])*self.lots[ticker]
                if not order.quantity:
                    order.status="below_lot"
                    order.reservation=order.cap_reservation=0
                self._log(order,"split_resized" if order.quantity else "below_lot",at,
                          queued_quantity_before_split=before,queued_quantity_after_split=order.quantity,
                          split_ratio=ratio)
        if ticker in self.marks:
            self.marks[ticker]/=ratio
        self.events.append({"status":"split","ticker":ticker,"ratio":ratio,"time":at.isoformat(),
                            "quantity_before":quantity_before,"quantity_after":position.quantity if position else 0,
                            "total_cost":position.cost if position else 0,
                            "average_cost_after":position.average_cost if position else None})

    def _log(self, order, status, at, **details):
        self.events.append({"event_id":order.event_id, "ticker":order.ticker,
                            "side":order.side, "status":status, "time":at.isoformat(),
                            "signal_time":order.signal_time.isoformat(),
                            "due_time":order.due_time.isoformat(),
                            "reason":order.reason, **details})

    def _affordable(self, budget, price, lot):
        units = max(0, floor(budget/(price*lot)))
        while units and units*lot*price + self.fee(units*lot*price) > budget + 1e-9:
            units -= 1
        return units*lot

    def _cash_notional(self,budget):
        """Invert the capped fee without treating fees as held market value."""
        budget=max(0,budget)
        uncapped=budget/(1+self.fee_rate)
        return uncapped if uncapped*self.fee_rate<=self.fee_cap else max(0,budget-self.fee_cap)

    def queue_buy(self, *, event_id, ticker, signal_time, due_time, slope, adx,
                  target, signal_price):
        if event_id in self.ids:
            return None
        if due_time < signal_time or not signal_time.tzinfo or not due_time.tzinfo:
            raise ValueError("Noncausal or naive order time")
        self.ids.add(event_id)
        lot = self.lots[ticker]
        self.mark(ticker, signal_price)
        # Queued notional constrains capacity; fee-inclusive reservations constrain cash.
        cap_room = max(0, self.cap-self.exposure-self.reserved_notional)
        available = max(0, self.cash-self.reserved)
        notional=min(max(0,target),cap_room,self._cash_notional(available))
        budget=min(available,notional+self.fee(notional))
        qty = min(max(0,floor((notional+1e-9)/(signal_price*lot)))*lot,
                  self._affordable(budget,signal_price,lot))
        reserve = budget if qty else 0
        order = Order(event_id,ticker,"buy",signal_time,due_time,slope,adx,target,qty,reserve,"entry")
        order.cap_reservation=notional if qty else 0
        if target <= 0:
            order.status = "nonpositive_target"
        elif not qty:
            order.status = ("below_lot" if target < lot*signal_price else
                            "cash_shortfall" if available < lot*signal_price+self.fee(lot*signal_price) else
                            "position_cap_shortfall")
        self.orders.append(order)
        self._log(order,order.status,signal_time,reservation=reserve,cap_reservation=order.cap_reservation,
                  signal_adx=adx,signal_slope=slope)
        return order

    def queue_exit(self, *, event_id, ticker, signal_time, due_time, reason):
        if event_id in self.ids:
            return None
        if due_time < signal_time or not signal_time.tzinfo or not due_time.tzinfo:
            raise ValueError("Noncausal or naive order time")
        self.ids.add(event_id)
        for o in self.orders:
            if o.ticker == ticker and o.side == "buy" and o.status == "queued":
                o.status = "canceled"
                self._log(o,"canceled",signal_time,cancellation_reason="aggregate_exit")
                o.reservation = 0
        order = Order(event_id,ticker,"sell",signal_time,due_time,0,None,0,0,0,reason)
        if not self.positions.get(ticker,Position()).quantity:
            order.status = "no_position"
        self.orders.append(order)
        self._log(order,order.status,signal_time)
        return order

    def execute(self, at: datetime, opens: dict[str,float], *, tax_year: int):
        """Use only opens observed at this instant, never forward-fill a fill."""
        for ticker, price in opens.items():
            self.mark(ticker,price)
        due = sorted((o for o in self.orders if o.status == "queued" and o.due_time <= at),
                     key=lambda o:(o.side != "sell", -o.slope, o.ticker, o.event_id))
        exited = set()
        for order in due:
            if order.status != "queued":
                continue
            if order.ticker not in opens:
                self._log(order,"missing_price",at)
                continue
            price = opens[order.ticker]
            if order.side == "sell":
                position = self.positions.get(order.ticker,Position())
                if not position.quantity:
                    order.status = "no_position"
                    self._log(order,"no_position",at)
                    continue
                quantity = position.quantity
                proceeds = quantity*price
                fee = self.fee(proceeds)
                pnl = proceeds-fee-position.cost
                year_profit = self.realized.get(tax_year,0)+pnl
                liability = max(0,year_profit)*self.tax_rate
                tax_delta = liability-self.tax_paid.get(tax_year,0)
                self.realized[tax_year], self.tax_paid[tax_year] = year_profit, liability
                self.cash += proceeds-fee-tax_delta
                self.fees += fee
                self.taxes += tax_delta
                self.trades.append({"ticker":order.ticker, "quantity":quantity,
                    "entry_time":position.first_fill.isoformat(), "exit_time":at.isoformat(),
                    "gross_pnl":proceeds-position.gross_cost, "after_fee_pnl":pnl,
                    "tax_delta":tax_delta, "after_tax_pnl":pnl-tax_delta,
                    "after_fee_return":pnl/position.cost,
                    "holding_seconds":(at-position.first_fill).total_seconds(), "exit_reason":order.reason})
                self.positions[order.ticker] = Position()
                exited.add(order.ticker)
                for pending in self.orders:
                    if pending is not order and pending.ticker == order.ticker and pending.status == "queued":
                        pending.status = "canceled"
                        pending.reservation = 0
                        self._log(pending,"canceled",at,cancellation_reason=
                                  "aggregate_exit_filled" if pending.side=="buy" else "superseded_aggregate_exit")
            else:
                if order.ticker in exited:
                    order.status = "canceled"
                    order.reservation = 0
                    self._log(order,"canceled",at,cancellation_reason="same_time_aggregate_exit")
                    continue
                other_reserved = self.reserved-order.reservation
                budget = min(order.reservation,self.cash-other_reserved)
                cap_room=max(0,self.cap-self.exposure)
                quantity = self._affordable(max(0,budget),price,self.lots[order.ticker])
                quantity = min(quantity, max(0,floor(min(order.target,cap_room)/(price*self.lots[order.ticker])))*self.lots[order.ticker])
                if self.policy.shrink_only:
                    quantity = min(quantity,order.quantity)
                if not quantity:
                    unit=price*self.lots[order.ticker]
                    order.status = ("below_lot" if order.target < unit else
                                    "cash_shortfall" if budget < unit+self.fee(unit) else
                                    "position_cap_shortfall")
                    order.reservation = 0
                    self._log(order,order.status,at,unexecuted_quantity=order.quantity)
                    continue
                fee = self.fee(quantity*price)
                cost = quantity*price+fee
                self.cash -= cost
                self.fees += fee
                p = self.positions.setdefault(order.ticker,Position())
                p.quantity += quantity
                p.cost += cost
                p.gross_cost += quantity*price
                p.first_fill = p.first_fill or at
            order.status = "filled"
            order.reservation = 0
            self._log(order,"filled",at,quantity=quantity,price=price,fee=fee,
                      signal_time=order.signal_time.isoformat(),due_time=order.due_time.isoformat(),
                      queued_quantity=order.quantity if order.side == "buy" else quantity,
                      unexecuted_quantity=order.quantity-quantity if order.side == "buy" else 0)
        if self.cash < -1e-7 or self.reserved > self.cash+1e-7:
            raise AssertionError("Cash/reservation invariant violated")

    def finish(self, at):
        for order in self.orders:
            if order.status == "queued":
                self._log(order,"unfilled_at_end",at)
        # Pending orders and residual positions remain visible; no invented liquidation.
