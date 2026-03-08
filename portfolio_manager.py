import pandas as pd
import yfinance as yf


def analyze_portfolio():

    try:

        df = pd.read_csv("portfolio.csv")

    except:

        return pd.DataFrame()

    results = []

    for _, row in df.iterrows():

        ticker = row["티커"]

        stock = yf.download(ticker, period="3mo")

        if stock.empty:
            continue

        current_price = stock["Close"].iloc[-1]

        buy_price = row["매수가"]

        profit = (current_price - buy_price) / buy_price * 100

        results.append({

            "종목": row["종목"],
            "현재가": round(current_price,2),
            "매수가": buy_price,
            "수익률": round(profit,2)

        })

    return pd.DataFrame(results)