import time
import pandas as pd

from data_loader import download_price
from model import train_predict
from signal_engine import generate_signal


DATA_DIR = "data"


# ----------------------------
# 코스피 종목 목록
# ----------------------------
def get_kospi_universe(limit=None):

    try:

        df = pd.read_csv(f"{DATA_DIR}/kospi_list.csv")

        if "name" not in df.columns or "ticker" not in df.columns:
            raise Exception("kospi_list.csv 형식 오류 (name,ticker 필요)")

        df = df.dropna().drop_duplicates(subset=["ticker"])
        df = df.reset_index(drop=True)

        if limit:
            df = df.head(limit)

        return df

    except Exception as e:

        print("종목 목록 로드 실패:", e)

        return pd.DataFrame(columns=["name", "ticker"])


# ----------------------------
# 전체 종목 스캐너
# ----------------------------
def run_scanner(limit=None):

    print("")
    print("===== 코스피 전체 AI 스캐너 시작 =====")

    universe = get_kospi_universe(limit)

    total = len(universe)

    print("스캔 대상 수:", total)

    if total == 0:

        print("⚠ 종목 데이터 없음")

        empty = pd.DataFrame()

        empty.to_csv(f"{DATA_DIR}/scanner_short_top.csv", index=False)
        empty.to_csv(f"{DATA_DIR}/scanner_long_top.csv", index=False)
        empty.to_csv(f"{DATA_DIR}/ai_short_top10.csv", index=False)
        empty.to_csv(f"{DATA_DIR}/ai_long_top10.csv", index=False)
        empty.to_csv(f"{DATA_DIR}/scanner_all_result.csv", index=False)
        empty.to_csv(f"{DATA_DIR}/scanner_score_top10.csv", index=False)

        return

    results = []

    for i, row in universe.iterrows():

        name = row["name"]
        ticker = row["ticker"]

        try:

            stock = download_price(ticker)

            if stock is None or stock.empty:
                print(f"[{i+1}/{total}] 데이터 없음:", name)
                continue

            if len(stock) < 120:
                print(f"[{i+1}/{total}] 데이터 부족:", name)
                continue

            prob_short, acc_short = train_predict(
                name,
                ticker,
                stock,
                None,
                1
            )

            prob_long, acc_long = train_predict(
                name,
                ticker,
                stock,
                None,
                20
            )

            signal = generate_signal(stock)

            results.append({

                "종목": name,
                "티커": ticker,
                "단타확률": round(prob_short * 100, 2),
                "중장기확률": round(prob_long * 100, 2),
                "단타정확도": round(acc_short * 100, 2),
                "중장기정확도": round(acc_long * 100, 2),
                "신호": signal

            })

            print(f"[{i+1}/{total}] 완료:", name)

            time.sleep(0.03)

        except Exception as e:

            print(f"[{i+1}/{total}] 분석 오류:", name, e)

            continue

    if len(results) == 0:

        print("⚠ 분석 결과 없음")

        empty = pd.DataFrame()

        empty.to_csv(f"{DATA_DIR}/scanner_short_top.csv", index=False)
        empty.to_csv(f"{DATA_DIR}/scanner_long_top.csv", index=False)
        empty.to_csv(f"{DATA_DIR}/ai_short_top10.csv", index=False)
        empty.to_csv(f"{DATA_DIR}/ai_long_top10.csv", index=False)
        empty.to_csv(f"{DATA_DIR}/scanner_all_result.csv", index=False)
        empty.to_csv(f"{DATA_DIR}/scanner_score_top10.csv", index=False)

        return

    df = pd.DataFrame(results)

    df.to_csv(
        f"{DATA_DIR}/scanner_all_result.csv",
        index=False,
        encoding="utf-8-sig"
    )

    short_df = df.sort_values("단타확률", ascending=False)
    long_df = df.sort_values("중장기확률", ascending=False)

    short_df.to_csv(
        f"{DATA_DIR}/scanner_short_top.csv",
        index=False,
        encoding="utf-8-sig"
    )

    long_df.to_csv(
        f"{DATA_DIR}/scanner_long_top.csv",
        index=False,
        encoding="utf-8-sig"
    )

    short_df.head(10).to_csv(
        f"{DATA_DIR}/ai_short_top10.csv",
        index=False,
        encoding="utf-8-sig"
    )

    long_df.head(10).to_csv(
        f"{DATA_DIR}/ai_long_top10.csv",
        index=False,
        encoding="utf-8-sig"
    )

    short_df.head(10).to_csv(
        f"{DATA_DIR}/scanner_score_top10.csv",
        index=False,
        encoding="utf-8-sig"
    )

    print("")
    print("CSV 파일 저장 완료")