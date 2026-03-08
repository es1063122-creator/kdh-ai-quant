import pandas as pd
import yfinance as yf


def analyze_watchlist():

    try:

        df = pd.read_csv("watchlist.csv")

    except:

        return pd.DataFrame()

    signals = []

    for _, row in df.iterrows():

        ticker = row["티커"]

        stock = yf.download(ticker, period="6mo")

        if stock.empty:
            continue

        ma5 = stock["Close"].rolling(5).mean().iloc[-1]

        ma20 = stock["Close"].rolling(20).mean().iloc[-1]

        if ma5 > ma20:
            signal = "BUY"
        else:
            signal = "WAIT"

        signals.append({

            "종목": row["종목"],
            "신호": signal

        })

    return pd.DataFrame(signals)