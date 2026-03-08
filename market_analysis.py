import FinanceDataReader as fdr
import pandas as pd


def get_market_state():

    try:

        kospi = fdr.DataReader("KS11")

        if kospi is None or kospi.empty:
            return "데이터 없음"

        close = kospi["Close"]

        ma20 = close.rolling(20).mean()
        ma60 = close.rolling(60).mean()

        close_last = float(close.iloc[-1])
        ma20_last = float(ma20.iloc[-1])
        ma60_last = float(ma60.iloc[-1])

        if close_last > ma20_last and ma20_last > ma60_last:
            return "상승장"

        elif close_last < ma20_last and ma20_last < ma60_last:
            return "하락장"

        else:
            return "횡보장"

    except Exception:

        # 시장 데이터 실패 시 기본값
        return "데이터 없음"