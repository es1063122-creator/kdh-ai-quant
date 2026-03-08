import time
import pandas as pd
import FinanceDataReader as fdr


def get_kospi_universe(limit=100):

    try:

        df = fdr.StockListing("KRX")

        df = df[df["Market"] == "KOSPI"]

        df = df[["Name", "Symbol"]]

        df = df.rename(columns={
            "Name": "name",
            "Symbol": "ticker"
        })

        df = df.reset_index(drop=True)

        if limit:
            df = df.head(limit)

        return df

    except Exception as e:

        print("종목 로드 실패:", e)

        return pd.DataFrame()


def detect_volume_surge(df):

    if len(df) < 30:
        return False, 0

    recent_vol = df["Volume"].iloc[-1]

    avg_vol = df["Volume"].iloc[-20:].mean()

    ratio = recent_vol / avg_vol

    if ratio > 3:
        return True, ratio

    return False, ratio


def run_realtime_scanner(limit=100):

    print("")
    print("===== 실시간 급등주 탐지 시작 =====")

    universe = get_kospi_universe(limit)

    results = []

    for i, row in universe.iterrows():

        name = row["name"]
        ticker = row["ticker"]

        try:

            df = fdr.DataReader(ticker)

            if df is None or df.empty:
                continue

            surge, ratio = detect_volume_surge(df)

            if surge:

                change = df["Close"].pct_change().iloc[-1] * 100

                results.append({
                    "종목": name,
                    "거래량배수": round(ratio, 2),
                    "등락률": round(change, 2)
                })

                print("급등 감지:", name, ratio)

        except:
            continue

    if len(results) == 0:

        print("급등 종목 없음")

        return pd.DataFrame()

    df = pd.DataFrame(results)

    df = df.sort_values(
        "거래량배수",
        ascending=False
    )

    print("")
    print("===== 급등 후보 =====")

    print(df.head(10))

    df.to_csv(
        "realtime_surge.csv",
        index=False,
        encoding="utf-8-sig"
    )

    return df