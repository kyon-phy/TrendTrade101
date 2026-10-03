"""Reconcile execution diagnostics and clearly labeled account statistics."""
from collections import Counter
from datetime import datetime
from .research import maximum_drawdown

def account_point(ledger,at):
    values=[p.quantity*ledger.marks[t] for t,p in ledger.positions.items() if p.quantity]
    exposure=sum(values)
    equity=ledger.equity
    return {"time":at.isoformat(),"equity":equity,"cash":ledger.cash,"exposure":exposure,
            "reserved":ledger.reserved,"fees":ledger.fees,"taxes":ledger.taxes,
            "capital_utilization":exposure/equity if equity else 0,
            "largest_position_equity_share":max(values,default=0)/equity if equity else 0,
            "position_hhi":sum((v/exposure)**2 for v in values) if exposure else 0}

def summarize(curve,initial_equity,fees,taxes,trades,events):
    final=curve[-1]["equity"] if curve else initial_equity
    seconds=weighted=0
    for left,right in zip(curve,curve[1:]):
        span=(datetime.fromisoformat(right["time"])-datetime.fromisoformat(left["time"])).total_seconds()
        if span<0:raise ValueError("Account curve is not chronological")
        seconds+=span;weighted+=span*left["capital_utilization"]
    event_ids=lambda statuses:{e["event_id"] for e in events if e["status"] in statuses and "event_id" in e}
    scheduled=lambda e:e.get("reason") in ("scheduled_daily_flatten","scheduled_monthly_flatten")
    failures={e["event_id"] for e in events if scheduled(e) and e["status"] in ("missing_price","unfilled_at_end")}
    return {"initial_equity":initial_equity,"final_equity":final,
            "after_tax_return":final/initial_equity-1,
            "after_fee_return":(final+taxes)/initial_equity-1,
            "gross_return":(final+taxes+fees)/initial_equity-1,
            "max_drawdown":maximum_drawdown([initial_equity]+[p["equity"] for p in curve]),
            "closed_trades":len(trades),"fees":fees,"taxes":taxes,"sparse":len(trades)<5,
            "win_rate":sum(t["after_fee_pnl"]>0 for t in trades)/len(trades) if trades else None,
            "average_trade_after_fee_return":sum(t["after_fee_return"] for t in trades)/len(trades) if trades else None,
            "average_holding_seconds":sum(t["holding_seconds"] for t in trades)/len(trades) if trades else None,
            "calendar_time_weighted_capital_utilization":weighted/seconds if seconds else 0,
            "maximum_capital_utilization":max((p["capital_utilization"] for p in curve),default=0),
            "maximum_single_position_equity_share":max((p["largest_position_equity_share"] for p in curve),default=0),
            "maximum_position_hhi":max((p["position_hhi"] for p in curve),default=0),
            "orders_with_missing_price":len(event_ids({"missing_price"})),
            "orders_unfilled_at_segment_end":len(event_ids({"unfilled_at_end"})),
            "below_lot_orders":len(event_ids({"below_lot"})),
            "cash_shortfall_orders":len(event_ids({"cash_shortfall"})),
            "position_cap_shortfall_orders":len(event_ids({"position_cap_shortfall"})),
            "canceled_orders":len(event_ids({"canceled"})),
            "unsuccessful_scheduled_liquidations":len(failures),
            "exit_reason_counts":dict(Counter(t["exit_reason"] for t in trades))}
