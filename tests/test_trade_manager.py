import pytest
from modules.trade_manager import TradeManager

class DummyRow:
    def __init__(self, rsi, adx, atr=1.0, macd_hist=0.0, close=100.0):
        self.rsi = rsi
        self.adx = adx
        self.atr = atr
        self.macd_hist = macd_hist
        self.close = close

@pytest.fixture
def tm():
    config = {
        "sell_threshold_percent": 50,
        "risk_per_trade": 0.02,
        "min_adx_operativita": 20
    }
    # saldo iniziale: 10 DOT, 1000 USDC
    return TradeManager(config, dot_balance=10, usdc_balance=1000)

def test_evaluate_buy(tm):
    row = DummyRow(rsi=15, adx=25)
    action = tm.evaluate(row, sentiment=0.1)
    assert action in ["buy_30", "buy_60", "buy_100"]

def test_evaluate_sell(tm):
    row = DummyRow(rsi=75, adx=25)
    action = tm.evaluate(row, sentiment=-0.1)
    assert action in ["sell_30", "sell_60", "sell_100"]

def test_evaluate_hold_low_adx(tm):
    row = DummyRow(rsi=10, adx=15)
    action = tm.evaluate(row, sentiment=1.0)
    assert action == "hold"
