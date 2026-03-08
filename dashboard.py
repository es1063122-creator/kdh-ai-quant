import streamlit as st
import pandas as pd
import os
import sys
import yfinance as yf
import mplfinance as mpf

# ======================
# CSS 로드
# ======================
def load_css():
    try:
        with open("style.css", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except:
        pass

load_css()

# ======================
# 경로 설정
# ======================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR,"data")

sys.path.append(BASE_DIR)
sys.path.append(os.path.join(BASE_DIR,"timing"))

from timing.entry_exit_engine import analyze_timing

HOLDINGS_FILE = os.path.join(DATA_DIR,"holdings.csv")
TIMING_FILE = os.path.join(DATA_DIR,"timing_signals.csv")

# ======================
# 차트 생성 함수
# ======================
def make_chart(df):

    try:

        df = df.rename(columns={
            "Open":"open",
            "High":"high",
            "Low":"low",
            "Close":"close",
            "Volume":"volume"
        })

        df = df[["open","high","low","close","volume"]].copy()

        for col in ["open","high","low","close","volume"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        # NaN 처리
        df = df.fillna(method="ffill")

        if len(df) < 10:
            return None

        fig,_ = mpf.plot(
            df,
            type="candle",
            mav=(5,20,60,120),
            volume=True,
            style="yahoo",
            returnfig=True
        )

        return fig

    except:
        return None

# ======================
# 기본 설정
# ======================
st.set_page_config(page_title="KDH AI QUANT TRADER",layout="wide")

st.markdown("""
<div class="card">
<div class="title">☕ KDH AI QUANT TRADER</div>
AI 기반 한국 주식 퀀트 트레이딩 시스템
</div>
""",unsafe_allow_html=True)

# ======================
# 보유종목 입력
# ======================
st.markdown('<div class="card">',unsafe_allow_html=True)

st.subheader("📌 보유주식 입력")

c1,c2,c3,c4 = st.columns(4)

name = c1.text_input("종목명")
ticker = c2.text_input("티커")
qty = c3.number_input("수량",min_value=1,step=1)
buy_price = c4.number_input("매입가",min_value=0)

if st.button("보유종목 저장"):

    new = pd.DataFrame([{
        "name":name,
        "ticker":str(ticker).zfill(6),
        "qty":qty,
        "buy_price":buy_price
    }])

    if os.path.exists(HOLDINGS_FILE):

        df = pd.read_csv(HOLDINGS_FILE)
        df = pd.concat([df,new])

    else:
        df = new

    df.to_csv(HOLDINGS_FILE,index=False)

    st.success("보유종목 저장 완료")

st.markdown('</div>',unsafe_allow_html=True)

# ======================
# 보유종목 보기
# ======================
st.markdown('<div class="card">',unsafe_allow_html=True)

st.subheader("📊 현재 보유종목")

try:

    holdings = pd.read_csv(HOLDINGS_FILE)
    st.dataframe(holdings,use_container_width=True)

except:

    st.warning("보유종목 없음")

st.markdown('</div>',unsafe_allow_html=True)

# ======================
# AI 분석
# ======================
st.markdown('<div class="card">',unsafe_allow_html=True)

st.subheader("📈 보유종목 AI 분석")

if st.button("보유종목 분석 실행"):

    try:

        holdings = pd.read_csv(HOLDINGS_FILE)

        results = []

        for _,row in holdings.iterrows():

            result = analyze_timing(
                row["name"],
                row["ticker"],
                row["qty"],
                row["buy_price"]
            )

            if result:
                results.append(result)

        if len(results)>0:

            result_df = pd.DataFrame(results)

            result_df.to_csv(TIMING_FILE,index=False)

            st.dataframe(result_df,use_container_width=True)

            st.subheader("📊 AI 분석 지표")

            score_df = pd.DataFrame({
                "항목":["RSI","거래량배수","AI점수"],
                "값":[
                    result_df["RSI"].iloc[0],
                    result_df["거래량배수"].iloc[0],
                    result_df["점수"].iloc[0]
                ]
            })

            st.bar_chart(score_df.set_index("항목"))

    except:

        st.error("AI 분석 실패")

st.markdown('</div>',unsafe_allow_html=True)

# ======================
# 종목 차트
# ======================
st.markdown('<div class="card">',unsafe_allow_html=True)

st.subheader("📈 종목 차트 (한국 HTS 스타일)")

stock_name = st.text_input("종목명 입력 (예: 삼성전자)")

if stock_name:

    try:

        stock_list = pd.read_excel("korea_stock_list.xlsx")

        name_col = "종목명" if "종목명" in stock_list.columns else "회사명"
        code_col = "종목코드"

        row = stock_list[stock_list[name_col] == stock_name]

        if len(row)>0:

            code = str(row.iloc[0][code_col]).zfill(6)

            ticker = code + ".KS"
            df = yf.download(ticker,period="6mo")

            if df.empty:
                ticker = code + ".KQ"
                df = yf.download(ticker,period="6mo")

            fig = make_chart(df)

            if fig:
                st.pyplot(fig)
            else:
                st.warning("차트 데이터 없음")

    except:

        st.error("차트 오류")

st.markdown('</div>',unsafe_allow_html=True)

# ======================
# 급등주 포트폴리오
# ======================
st.markdown('<div class="card">',unsafe_allow_html=True)

st.subheader("🚀 AI 급등주 포트폴리오")

surge_df = pd.DataFrame()

try:

    surge_df = pd.read_csv("surge_portfolio.csv")
    st.dataframe(surge_df,use_container_width=True)

except:

    st.warning("포트폴리오 없음")

st.subheader("📈 급등주 차트 보기")

try:

    if not surge_df.empty:

        stock_choice = st.selectbox("급등주 선택",surge_df["종목"])

        if stock_choice:

            stock_list = pd.read_excel("korea_stock_list.xlsx")

            name_col = "종목명" if "종목명" in stock_list.columns else "회사명"
            code_col = "종목코드"

            row = stock_list[stock_list[name_col] == stock_choice]

            if len(row)>0:

                code = str(row.iloc[0][code_col]).zfill(6)

                ticker = code + ".KS"
                df = yf.download(ticker,period="6mo")

                if df.empty:
                    ticker = code + ".KQ"
                    df = yf.download(ticker,period="6mo")

                fig = make_chart(df)

                if fig:
                    st.pyplot(fig)
                else:
                    st.warning("차트 데이터 없음")

except:

    st.warning("급등주 차트 오류")

st.markdown('</div>',unsafe_allow_html=True)

# ======================
# 단타 TOP10
# ======================
st.markdown('<div class="card">',unsafe_allow_html=True)

st.subheader("📈 AI 단타 TOP10")

try:

    df = pd.read_csv("ai_short_top10.csv")
    st.dataframe(df,use_container_width=True)

except:

    st.warning("데이터 없음")

st.markdown('</div>',unsafe_allow_html=True)

# ======================
# 중장기 TOP10
# ======================
st.markdown('<div class="card">',unsafe_allow_html=True)

st.subheader("📊 AI 중장기 TOP10")

try:

    df = pd.read_csv("ai_long_top10.csv")
    st.dataframe(df,use_container_width=True)

except:

    st.warning("데이터 없음")

st.markdown('</div>',unsafe_allow_html=True)

# ======================
# 전체 스캐너
# ======================
st.markdown('<div class="card">',unsafe_allow_html=True)

st.subheader("🔎 코스피 전체 AI 스캔")

try:

    df = pd.read_csv("data/scanner_all_result.csv")
    st.dataframe(df,use_container_width=True)

except:

    st.warning("스캐너 결과 없음")

st.markdown('</div>',unsafe_allow_html=True)

st.caption("KDH AI QUANT DASHBOARD")