import pandas as pd
from entry_exit_engine import analyze_timing

DATA_DIR = "data"


def run_holding_monitor():

    print("")
    print("===== 보유종목 타이밍 분석 =====")

    holdings = pd.read_csv(f"{DATA_DIR}/holdings.csv")

    results = []

    for i, row in holdings.iterrows():

        name = row["name"]
        ticker = row["ticker"]
        qty = row["qty"]
        buy_price = row["buy_price"]

        try:

            result = analyze_timing(name, ticker, qty, buy_price)

            if result:
                results.append(result)
                print("분석 완료:", name)

        except Exception as e:
            print("오류:", name, e)

    if len(results) == 0:
        print("분석 결과 없음")
        return

    df = pd.DataFrame(results)

    df = df.sort_values("점수", ascending=False)

    print("")
    print(df)

    df.to_csv(
        f"{DATA_DIR}/timing_signals.csv",
        index=False,
        encoding="utf-8-sig"
    )

    print("")
    print("저장 완료: data/timing_signals.csv")


if __name__ == "__main__":
    run_holding_monitor()