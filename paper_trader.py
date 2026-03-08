import pandas as pd
import yfinance as yf


def analyze_paper_trade():

    try:

        df = pd.read_csv("paper_trade.csv")

    except:

        return pd.DataFrame()

    results = []

    for _, row in df.iterrows():

        ticker = row["티커"]

        stock = yf.download(ticker, period="1mo")

        if stock.empty:
            continue

        current = stock["Close"].iloc[-1]

        buy = row["매수가"]

        profit = (current - buy) / buy * 100

        results.append({

            "종목": row["종목"],
            "현재가": round(current,2),
            "수익률": round(profit,2)

        })

    return pd.DataFrame(results)