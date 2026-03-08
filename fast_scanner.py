import pandas as pd
import yfinance as yf
from concurrent.futures import ThreadPoolExecutor, as_completed
import os
import warnings

warnings.filterwarnings("ignore")

DATA_DIR = "data"

# ===============================
# 종목 리스트 로드
# ===============================
def load_universe():

    file = os.path.join(DATA_DIR, "korea_stock_list.xlsx")

    df = pd.read_excel(file)

    df = df.rename(columns={
        "회사명": "name",
        "종목코드": "ticker"
    })

    df["ticker"] = df["ticker"].astype(str).str.zfill(6)

    # 숫자 6자리만 필터
    df = df[df["ticker"].str.match(r"^[0-9]{6}$")]

    df["yf"] = df["ticker"] + ".KS"

    return df


# ===============================
# 데이터 다운로드
# ===============================
def download_price(ticker):

    try:

        df = yf.download(
            ticker,
            period="3mo",
            interval="1d",
            progress=False,
            threads=False
        )

        if len(df) < 30:
            return None

        return df

    except:
        return None


# ===============================
# 1차 필터
# ===============================
def quick_filter(stock):

    try:

        vol = stock["Volume"].tail(20).mean()

        if vol < 10000:
            return False

        ret3 = stock["Close"].pct_change(3).iloc[-1]

        if ret3 < 0.01:
            return False

        return True

    except:
        return False


# ===============================
# 종목 분석
# ===============================
def analyze_stock(row):

    ticker = row["yf"]
    name = row["name"]

    stock = download_price(ticker)

    if stock is None:
        return None

    if not quick_filter(stock):
        return None

    price = stock["Close"].iloc[-1]

    return {
        "name": name,
        "ticker": ticker,
        "price": round(price, 2)
    }


# ===============================
# 스캐너 실행
# ===============================
def run_scan():

    print("===== KDH FAST SCANNER =====")

    universe = load_universe()

    print("전체 종목:", len(universe))

    results = []

    with ThreadPoolExecutor(max_workers=30) as executor:

        futures = [
            executor.submit(analyze_stock, row)
            for _, row in universe.iterrows()
        ]

        for future in as_completed(futures):

            r = future.result()

            if r:
                results.append(r)

    df = pd.DataFrame(results)

    out = os.path.join(DATA_DIR, "scanner_results.csv")

    df.to_csv(out, index=False)

    print("검색된 종목:", len(df))
    print("결과 저장:", out)


if __name__ == "__main__":
    run_scan()