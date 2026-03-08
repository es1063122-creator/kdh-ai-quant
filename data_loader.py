import FinanceDataReader as fdr
import pandas as pd
import numpy as np


# -----------------------------
# 주가 다운로드
# -----------------------------
def download_price(ticker):

    try:

        ticker = ticker.replace(".KS", "")

        df = fdr.DataReader(ticker)

        if df is None or df.empty:
            return None

        return df

    except:

        return None


# -----------------------------
# 수익률 계산
# -----------------------------
def safe_pct_change(series, periods=1):

    return series.pct_change(periods).replace(
        [np.inf, -np.inf],
        np.nan
    )


# -----------------------------
# 시장 데이터
# -----------------------------
def build_market_frame():

    try:

        kospi = fdr.DataReader("KS11")

        df = pd.DataFrame()

        df["kospi"] = safe_pct_change(kospi["Close"])

        return df

    except:

        return pd.DataFrame()