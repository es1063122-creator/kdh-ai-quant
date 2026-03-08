import pandas as pd
import numpy as np


def compute_rsi(series, period=14):

    delta = series.diff()

    gain = delta.clip(lower=0).rolling(period).mean()

    loss = (-delta.clip(upper=0)).rolling(period).mean()

    rs = gain / loss.replace(0, np.nan)

    return 100 - (100 / (1 + rs))


def add_features(stock_df, market_df, hold_days):

    df = stock_df.copy()

    df["ret1"] = df["Close"].pct_change()

    df["ma5"] = df["Close"].rolling(5).mean()

    df["ma20"] = df["Close"].rolling(20).mean()

    df["vol"] = df["ret1"].rolling(5).std()

    df["rsi"] = compute_rsi(df["Close"])

    merged = df.join(market_df, how="left")

    future_return = merged["Close"].shift(-hold_days) / merged["Close"] - 1

    merged["target"] = (future_return > 0).astype(int)

    return merged