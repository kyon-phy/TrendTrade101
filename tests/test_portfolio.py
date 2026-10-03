import unittest
from datetime import datetime,timedelta,timezone
from trendtrade101.portfolio import Ledger,LedgerPolicy

T=datetime(2026,1,2,10,tzinfo=timezone.utc)
def account(capital=100000,lot=1,tax=.20315):
    return Ledger(capital=capital,position_cap=capital,fee_rate=.00495,fee_cap=22,
                  tax_rate=tax,lots={"AAA":lot,"BBB":lot},policy=LedgerPolicy("market_value",True,"realization_accrual",False))
def buy(a,event="a",ticker="AAA",price=100,target=1000,at=T,due=None,slope=1):
    return a.queue_buy(event_id=event,ticker=ticker,signal_time=at,due_time=due or at+timedelta(minutes=20),
                       slope=slope,adx=30,target=target,signal_price=price)
def sell(a,event="exit",ticker="AAA",at=T+timedelta(hours=1)):
    return a.queue_exit(event_id=event,ticker=ticker,signal_time=at,due_time=at,reason="test")

class PortfolioTests(unittest.TestCase):
    def test_flat_scheduled_exit_cancels_buys_without_a_lingering_sell(self):
        a=account();pending=buy(a)
        order=sell(a,at=T+timedelta(minutes=1))
        self.assertEqual(pending.status,"canceled")
        self.assertEqual(order.status,"no_position")
        buy(a,event="later",at=T+timedelta(hours=2))
        a.execute(T+timedelta(hours=3),{"AAA":100},tax_year=2026)
        self.assertEqual(a.positions["AAA"].quantity,10)

    def test_filled_aggregate_exit_cancels_duplicate_future_exits(self):
        a=account();buy(a)
        a.execute(T+timedelta(minutes=20),{"AAA":100},tax_year=2026)
        first=sell(a)
        later=a.queue_exit(event_id="later-exit",ticker="AAA",signal_time=T+timedelta(hours=1),
                           due_time=T+timedelta(hours=2),reason="scheduled")
        a.execute(T+timedelta(hours=1),{"AAA":100},tax_year=2026)
        self.assertEqual(first.status,"filled")
        self.assertEqual(later.status,"canceled")

    def test_delay_and_fill_open(self):
        a=account();buy(a)
        a.execute(T+timedelta(minutes=19),{"AAA":110},tax_year=2026)
        self.assertFalse(a.positions)
        a.execute(T+timedelta(minutes=20),{"AAA":110},tax_year=2026)
        self.assertEqual(a.positions["AAA"].quantity,9)
        self.assertAlmostEqual(a.cash,100000-990-990*.00495)

    def test_price_drop_never_increases_signal_quantity(self):
        a=account();buy(a)
        a.execute(T+timedelta(minutes=20),{"AAA":50},tax_year=2026)
        self.assertEqual(a.positions["AAA"].quantity,10)
        self.assertEqual(a.reserved,0)

    def test_cash_reserved_once_and_duplicate_is_idempotent(self):
        a=account(capital=1100);buy(a)
        reserved=a.reserved
        self.assertIsNone(buy(a))
        self.assertEqual(a.reserved,reserved)
        buy(a,event="b",ticker="BBB")
        self.assertLessEqual(a.reserved,a.cash)
        a.execute(T+timedelta(minutes=20),{"AAA":100,"BBB":100},tax_year=2026)
        self.assertGreaterEqual(a.cash,0)

    def test_target_plus_fee_reservation_retains_rounding_remainder(self):
        a=account()
        o=buy(a,price=101,target=1000)
        self.assertEqual(o.quantity,9)
        self.assertAlmostEqual(o.reservation,1000+a.fee(1000))
        a.execute(T+timedelta(minutes=20),{"AAA":102},tax_year=2026)
        self.assertEqual(a.positions["AAA"].quantity,9)
        self.assertEqual(a.reserved,0)

    def test_missing_price_retains_pending_order(self):
        a=account();o=buy(a)
        a.execute(T+timedelta(minutes=20),{},tax_year=2026)
        self.assertEqual(o.status,"queued")
        self.assertEqual(a.events[-1]["status"],"missing_price")
        a.execute(T+timedelta(minutes=25),{"AAA":100},tax_year=2026)
        self.assertEqual(o.status,"filled")

    def test_pyramiding_and_exit_cancels_later_pending_buys(self):
        a=account();buy(a)
        a.execute(T+timedelta(minutes=20),{"AAA":100},tax_year=2026)
        buy(a,event="b",at=T+timedelta(minutes=30))
        a.execute(T+timedelta(minutes=50),{"AAA":100},tax_year=2026)
        self.assertEqual(a.positions["AAA"].quantity,20)
        o=buy(a,event="pending",at=T+timedelta(minutes=51))
        sell(a)
        self.assertEqual(o.status,"canceled")
        a.execute(T+timedelta(hours=1),{"AAA":105},tax_year=2026)
        self.assertEqual(a.positions["AAA"].quantity,0)
        self.assertEqual(a.reserved,0)
        self.assertEqual(a.trades[0]["quantity"],20)

    def test_exit_fill_cancels_buys_created_during_delay(self):
        a=account();buy(a)
        a.execute(T+timedelta(minutes=20),{"AAA":100},tax_year=2026)
        a.queue_exit(event_id="x",ticker="AAA",signal_time=T+timedelta(minutes=30),
                     due_time=T+timedelta(minutes=50),reason="histogram")
        o=buy(a,event="new",at=T+timedelta(minutes=40))
        a.execute(T+timedelta(minutes=50),{"AAA":100},tax_year=2026)
        self.assertEqual(o.status,"canceled")
        self.assertEqual(a.positions["AAA"].quantity,0)

    def test_whole_japan_lot_and_fee_limit(self):
        a=account(capital=16000000,lot=100)
        o=buy(a,price=12000,target=1066666)
        self.assertEqual(o.status,"below_lot")
        self.assertEqual(a.fee(100000),22)

    def test_tax_refund_is_limited_to_current_year_tax(self):
        a=account();buy(a)
        a.execute(T+timedelta(minutes=20),{"AAA":100},tax_year=2026)
        sell(a);a.execute(T+timedelta(hours=1),{"AAA":200},tax_year=2026)
        accrued=a.taxes
        self.assertGreater(accrued,0)
        buy(a,event="b",at=T+timedelta(hours=2),price=200,target=2000)
        a.execute(T+timedelta(hours=3),{"AAA":200},tax_year=2026)
        sell(a,event="s2",at=T+timedelta(hours=4))
        a.execute(T+timedelta(hours=4),{"AAA":1},tax_year=2026)
        self.assertAlmostEqual(a.taxes,0)
        self.assertEqual(a.trades[-1]["tax_delta"],-accrued)
        self.assertLess(a.realized[2026],0)

    def test_no_fictitious_year_loss_subsidy(self):
        a=account();buy(a)
        a.execute(T+timedelta(minutes=20),{"AAA":100},tax_year=2026)
        sell(a);a.execute(T+timedelta(hours=1),{"AAA":50},tax_year=2027)
        self.assertEqual(a.taxes,0)

    def test_unfilled_exit_preserves_actual_position(self):
        a=account();buy(a)
        a.execute(T+timedelta(minutes=20),{"AAA":100},tax_year=2026)
        sell(a);a.execute(T+timedelta(hours=1),{},tax_year=2026)
        a.finish(T+timedelta(hours=2))
        self.assertEqual(a.positions["AAA"].quantity,10)
        self.assertEqual(a.events[-1]["status"],"unfilled_at_end")
