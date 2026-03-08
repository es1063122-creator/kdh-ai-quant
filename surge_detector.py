import time
import pandas as pd

from data_loader import download_price
from model import train_predict
from flow_analysis import get_foreign_flow
from news_signal import get_news_signal

DATA_DIR="data"

# -----------------------------
# 거래량 상위 10% 필터
# -----------------------------
def filter_top_volume(universe):

    volumes=[]

    for _,row in universe.iterrows():

        ticker=row["ticker"]

        try:

            df=download_price(ticker)

            if df is None or df.empty:
                continue

            vol=df["Volume"].iloc[-1]

            volumes.append({
                "name":row["name"],
                "ticker":ticker,
                "volume":vol
            })

        except:
            continue

    vol_df=pd.DataFrame(volumes)

    if vol_df.empty:
        return pd.DataFrame()

    top=vol_df.nlargest(int(len(vol_df)*0.1),"volume")

    return top


# -----------------------------
# 급등주 탐지
# -----------------------------
def run_surge_detector(limit=200, top_n=10):

    print("")
    print("===== 단타용 AI 급등주 탐지 시작 =====")

    universe=pd.read_csv(f"{DATA_DIR}/kospi_list.csv").head(limit)

    # 거래량 상위 10%
    universe=filter_top_volume(universe)

    results=[]

    for i,row in universe.iterrows():

        name=row["name"]
        ticker=row["ticker"]

        try:

            stock=download_price(ticker)

            if stock is None or len(stock)<120:
                continue

            prob,acc=train_predict(name,ticker,stock,None,1)

            flow=get_foreign_flow(ticker)

            news=get_news_signal(name)

            score=(prob*100*0.5)+(acc*100*0.3)+(flow*5)+(news*5)

            results.append({

                "종목":name,
                "티커":ticker,
                "AI상승확률(%)":round(prob*100,2),
                "백테스트정확도(%)":round(acc*100,2),
                "외국인수급":flow,
                "뉴스점수":news,
                "급등점수":round(score,2)

            })

            print(f"[{i+1}] 완료:",name)

            time.sleep(0.02)

        except Exception as e:

            print("오류:",name,e)

    if len(results)==0:

        print("급등 후보 없음")
        return pd.DataFrame(),pd.DataFrame()

    df=pd.DataFrame(results)

    df=df.sort_values("급등점수",ascending=False)

    top_df=df.head(top_n)

    df.to_csv(
        f"{DATA_DIR}/surge_candidates.csv",
        index=False,
        encoding="utf-8-sig"
    )

    top_df.to_csv(
        f"{DATA_DIR}/surge_top10.csv",
        index=False,
        encoding="utf-8-sig"
    )

    print("")
    print("급등주 TOP10")
    print(top_df)

    return df,top_df