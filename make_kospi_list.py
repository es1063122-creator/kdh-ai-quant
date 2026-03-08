from pykrx import stock
import pandas as pd
import datetime

today = datetime.datetime.today().strftime("%Y%m%d")

print("코스피 종목 다운로드 중...")

tickers = stock.get_market_ticker_list(today, market="KOSPI")

rows = []

for t in tickers:

    name = stock.get_market_ticker_name(t)

    rows.append({
        "name": name,
        "ticker": t + ".KS"
    })

df = pd.DataFrame(rows)

df.to_csv("kospi_list.csv", index=False, encoding="utf-8-sig")

print("완료")
print("종목 수:", len(df))