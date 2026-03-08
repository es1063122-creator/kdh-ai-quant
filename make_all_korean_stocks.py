import yfinance as yf
import pandas as pd
from tqdm import tqdm

data = []

# 000001 ~ 999999 중에서 실제 존재하는 종목 찾기
for i in tqdm(range(1, 999999)):

    code = str(i).zfill(6)

    for suffix in [".KS", ".KQ"]:   # 코스피 / 코스닥
        ticker = code + suffix

        try:
            info = yf.Ticker(ticker).info

            name = info.get("shortName")

            if name:
                market = "KOSPI" if suffix == ".KS" else "KOSDAQ"

                data.append({
                    "name": name,
                    "ticker": ticker,
                    "code": code,
                    "market": market
                })

        except:
            pass

# 엑셀 저장
df = pd.DataFrame(data)
df.to_excel("korea_stock_list.xlsx", index=False)

print("총 종목수:", len(df))
print("엑셀 생성 완료")