import os
import sys
import pandas as pd
import streamlit as st

# -------------------------------------------------
# 경로 설정
# -------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
TIMING_DIR = os.path.join(BASE_DIR, "timing")
STYLE_FILE = os.path.join(BASE_DIR, "style.css")

if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

# timing 폴더 import 가능하게
if TIMING_DIR not in sys.path:
    sys.path.append(TIMING_DIR)

from timing.entry_exit_engine import analyze_timing

# -------------------------------------------------
# 파일 경로
# -------------------------------------------------
HOLDINGS_FILE = os.path.join(DATA_DIR, "holdings.csv")
TIMING_SIGNALS_FILE = os.path.join(DATA_DIR, "timing_signals.csv")
SURGE_PORTFOLIO_FILE = os.path.join(BASE_DIR, "surge_portfolio.csv")
AI_SHORT_TOP10_FILE = os.path.join(BASE_DIR, "ai_short_top10.csv")
AI_LONG_TOP10_FILE = os.path.join(BASE_DIR, "ai_long_top10.csv")
SCANNER_RESULT_FILE = os.path.join(DATA_DIR, "scanner_all_result.csv")

# -------------------------------------------------
# 기본 설정
# -------------------------------------------------
st.set_page_config(
    page_title="KDH AI QUANT TRADER",
    page_icon="📈",
    layout="wide"
)

os.makedirs(DATA_DIR, exist_ok=True)

# -------------------------------------------------
# 스타일 로드
# -------------------------------------------------
def load_css():
    base_css = """
    <style>
    .block-container {
        padding-top: 1.4rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }
    .kdh-card {
        background: #ffffff;
        border-radius: 16px;
        padding: 18px 18px 14px 18px;
        box-shadow: 0 6px 20px rgba(0,0,0,0.06);
        margin-bottom: 18px;
        border: 1px solid rgba(0,0,0,0.04);
    }
    .kdh-title {
        color: #006241;
        font-size: 28px;
        font-weight: 800;
        margin-bottom: 6px;
    }
    .kdh-sub {
        color: #666;
        font-size: 14px;
        margin-bottom: 0;
    }
    .signal-buy {
        color: #00a862;
        font-weight: 800;
    }
    .signal-hold {
        color: #1f6feb;
        font-weight: 800;
    }
    .signal-sell {
        color: #d97706;
        font-weight: 800;
    }
    .signal-stop {
        color: #d32f2f;
        font-weight: 800;
    }
    .section-gap {
        margin-top: 8px;
        margin-bottom: 8px;
    }
    </style>
    """
    st.markdown(base_css, unsafe_allow_html=True)

    if os.path.exists(STYLE_FILE):
        try:
            css = open(STYLE_FILE, "r", encoding="utf-8").read()
            st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
        except Exception:
            pass


load_css()

# -------------------------------------------------
# 공통 함수
# -------------------------------------------------
def read_csv_safe(path: str, columns: list[str] | None = None) -> pd.DataFrame:
    if os.path.exists(path):
        try:
            df = pd.read_csv(path)
            return df
        except Exception:
            pass

    if columns:
        return pd.DataFrame(columns=columns)
    return pd.DataFrame()


def save_holdings(df: pd.DataFrame):
    df.to_csv(HOLDINGS_FILE, index=False, encoding="utf-8-sig")


def load_holdings() -> pd.DataFrame:
    default_cols = ["name", "ticker", "qty", "buy_price"]
    df = read_csv_safe(HOLDINGS_FILE, columns=default_cols)

    for col in default_cols:
        if col not in df.columns:
            df[col] = []

    if not df.empty:
        df["name"] = df["name"].astype(str).str.strip()
        df["ticker"] = df["ticker"].astype(str).str.replace(".0", "", regex=False).str.zfill(6)
        df["qty"] = pd.to_numeric(df["qty"], errors="coerce").fillna(0).astype(int)
        df["buy_price"] = pd.to_numeric(df["buy_price"], errors="coerce").fillna(0)

    return df[default_cols]


def add_holding(name: str, ticker: str, qty: int, buy_price: float):
    name = str(name).strip()
    ticker = str(ticker).strip().replace(".0", "").zfill(6)

    if not name:
        raise ValueError("종목명을 입력하세요.")
    if not ticker.isdigit() or len(ticker) != 6:
        raise ValueError("티커는 6자리 숫자로 입력하세요. 예: 005930")
    if qty <= 0:
        raise ValueError("수량은 1 이상이어야 합니다.")
    if buy_price <= 0:
        raise ValueError("매입가는 0보다 커야 합니다.")

    df = load_holdings()

    new_row = pd.DataFrame([{
        "name": name,
        "ticker": ticker,
        "qty": int(qty),
        "buy_price": float(buy_price)
    }])

    df = pd.concat([df, new_row], ignore_index=True)
    save_holdings(df)


def delete_holding_by_index(idx: int):
    df = load_holdings()
    if df.empty:
        return
    if 0 <= idx < len(df):
        df = df.drop(index=idx).reset_index(drop=True)
        save_holdings(df)


def clear_holdings():
    save_holdings(pd.DataFrame(columns=["name", "ticker", "qty", "buy_price"]))


def signal_to_html(signal: str) -> str:
    signal = str(signal)
    if signal in ["강한매수", "추가매수 고려"]:
        return f'<span class="signal-buy">{signal}</span>'
    if signal in ["보유", "보유 유지"]:
        return f'<span class="signal-hold">{signal}</span>'
    if signal in ["분할매도", "분할매도 고려"]:
        return f'<span class="signal-sell">{signal}</span>'
    if signal in ["손절경고", "손절 경고"]:
        return f'<span class="signal-stop">{signal}</span>'
    return signal


def style_signal_df(df: pd.DataFrame) -> pd.io.formats.style.Styler:
    def color_signal(val):
        val = str(val)
        if val in ["강한매수", "추가매수 고려"]:
            return "color:#00a862;font-weight:800;"
        if val in ["보유", "보유 유지"]:
            return "color:#1f6feb;font-weight:800;"
        if val in ["분할매도", "분할매도 고려"]:
            return "color:#d97706;font-weight:800;"
        if val in ["손절경고", "손절 경고"]:
            return "color:#d32f2f;font-weight:800;"
        return ""

    if "신호" in df.columns:
        return df.style.map(color_signal, subset=["신호"])
    return df.style


def run_holdings_analysis() -> pd.DataFrame:
    holdings = load_holdings()

    if holdings.empty:
        return pd.DataFrame()

    results = []

    for _, row in holdings.iterrows():
        try:
            result = analyze_timing(
                row["name"],
                row["ticker"],
                row["qty"],
                row["buy_price"]
            )
            if result:
                results.append(result)
        except Exception as e:
            results.append({
                "종목": row["name"],
                "티커": str(row["ticker"]).zfill(6),
                "현재가": None,
                "보유수량": row["qty"],
                "매입가": row["buy_price"],
                "수익률(%)": None,
                "RSI": None,
                "거래량배수": None,
                "점수": None,
                "신호": f"오류: {e}"
            })

    if not results:
        return pd.DataFrame()

    result_df = pd.DataFrame(results)

    if "점수" in result_df.columns:
        result_df["점수"] = pd.to_numeric(result_df["점수"], errors="coerce")
        result_df = result_df.sort_values("점수", ascending=False, na_position="last").reset_index(drop=True)

    result_df.to_csv(TIMING_SIGNALS_FILE, index=False, encoding="utf-8-sig")
    return result_df


def metric_safe(df: pd.DataFrame, col: str, func="mean", round_digits=2):
    if df.empty or col not in df.columns:
        return "-"
    s = pd.to_numeric(df[col], errors="coerce").dropna()
    if s.empty:
        return "-"
    if func == "mean":
        return round(float(s.mean()), round_digits)
    if func == "max":
        return round(float(s.max()), round_digits)
    if func == "min":
        return round(float(s.min()), round_digits)
    return "-"


# -------------------------------------------------
# 세션 상태
# -------------------------------------------------
if "analysis_df" not in st.session_state:
    st.session_state.analysis_df = read_csv_safe(TIMING_SIGNALS_FILE)

# -------------------------------------------------
# 헤더
# -------------------------------------------------
st.markdown(
    """
    <div class="kdh-card">
        <div class="kdh-title">☕ KDH AI QUANT TRADER</div>
        <p class="kdh-sub">보유주식 입력 · 매수/매도 타이밍 분석 · 급등주/스캐너 결과 통합 대시보드</p>
    </div>
    """,
    unsafe_allow_html=True
)

# -------------------------------------------------
# 상단 입력 영역
# -------------------------------------------------
st.markdown('<div class="kdh-card">', unsafe_allow_html=True)
st.subheader("📌 보유주식 입력")

with st.form("holding_input_form", clear_on_submit=True):
    c1, c2, c3, c4 = st.columns(4)
    name = c1.text_input("종목명", placeholder="예: 삼성전자")
    ticker = c2.text_input("티커", placeholder="예: 005930")
    qty = c3.number_input("수량", min_value=1, step=1, value=1)
    buy_price = c4.number_input("매입가", min_value=1.0, step=100.0, value=1000.0)

    submit = st.form_submit_button("보유종목 저장", use_container_width=True)

    if submit:
        try:
            add_holding(name, ticker, int(qty), float(buy_price))
            st.success("보유종목 저장 완료")
            st.rerun()
        except Exception as e:
            st.error(f"저장 실패: {e}")

st.markdown("</div>", unsafe_allow_html=True)

# -------------------------------------------------
# 보유종목 관리
# -------------------------------------------------
holdings_df = load_holdings()

left, right = st.columns([1.55, 1])

with left:
    st.markdown('<div class="kdh-card">', unsafe_allow_html=True)
    st.subheader("📋 현재 보유종목")

    if holdings_df.empty:
        st.info("등록된 보유종목이 없습니다.")
    else:
        view_df = holdings_df.copy()
        view_df.index = view_df.index + 1
        st.dataframe(view_df, use_container_width=True, height=320)

        del_col1, del_col2 = st.columns([1, 2])
        with del_col1:
            delete_index = st.number_input(
                "삭제할 행 번호",
                min_value=1,
                max_value=len(holdings_df),
                step=1,
                value=1
            )
        with del_col2:
            st.write("")
            st.write("")
            if st.button("선택 행 삭제", use_container_width=True):
                delete_holding_by_index(int(delete_index) - 1)
                st.success("선택 행 삭제 완료")
                st.rerun()

        if st.button("전체 보유종목 비우기", use_container_width=True):
            clear_holdings()
            st.success("전체 보유종목 삭제 완료")
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

with right:
    st.markdown('<div class="kdh-card">', unsafe_allow_html=True)
    st.subheader("⚙ 보유종목 AI 분석")

    if st.button("보유종목 분석 실행", use_container_width=True):
        if holdings_df.empty:
            st.warning("먼저 보유종목을 입력하세요.")
        else:
            with st.spinner("AI 분석 중입니다..."):
                analysis_df = run_holdings_analysis()
                st.session_state.analysis_df = analysis_df

            if analysis_df.empty:
                st.warning("분석 결과 없음")
            else:
                st.success("분석 완료")

    analysis_df = st.session_state.analysis_df

    m1, m2, m3 = st.columns(3)
    m1.metric("보유종목 수", len(holdings_df))
    m2.metric("평균 수익률", metric_safe(analysis_df, "수익률(%)"))
    m3.metric("평균 점수", metric_safe(analysis_df, "점수"))

    st.markdown("</div>", unsafe_allow_html=True)

# -------------------------------------------------
# 분석 결과
# -------------------------------------------------
st.markdown('<div class="kdh-card">', unsafe_allow_html=True)
st.subheader("📈 보유종목 AI 분석 결과")

analysis_df = st.session_state.analysis_df

if analysis_df is None or analysis_df.empty:
    st.info("분석 결과가 없습니다. '보유종목 분석 실행' 버튼을 눌러주세요.")
else:
    show_df = analysis_df.copy()

    if "신호" in show_df.columns:
        styled = style_signal_df(show_df)
        st.dataframe(styled, use_container_width=True, height=380)
    else:
        st.dataframe(show_df, use_container_width=True, height=380)

    if "점수" in show_df.columns:
        chart_df = show_df.copy()
        chart_df["점수"] = pd.to_numeric(chart_df["점수"], errors="coerce")
        chart_df = chart_df.dropna(subset=["점수"])
        if not chart_df.empty and "종목" in chart_df.columns:
            st.subheader("점수 차트")
            st.bar_chart(chart_df.set_index("종목")[["점수"]])

st.markdown("</div>", unsafe_allow_html=True)

# -------------------------------------------------
# 기존 대시보드 데이터
# -------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "🚀 AI 급등주 포트폴리오",
    "📈 AI 단타 TOP10",
    "📊 AI 중장기 TOP10",
    "🔎 코스피 전체 AI 스캔"
])

with tab1:
    st.subheader("🚀 AI 급등주 포트폴리오")
    df = read_csv_safe(SURGE_PORTFOLIO_FILE)
    if df.empty:
        st.warning("포트폴리오 없음")
    else:
        st.dataframe(df, use_container_width=True, height=420)

with tab2:
    st.subheader("📈 AI 단타 TOP10")
    df = read_csv_safe(AI_SHORT_TOP10_FILE)
    if df.empty:
        st.warning("데이터 없음")
    else:
        st.dataframe(df, use_container_width=True, height=420)

with tab3:
    st.subheader("📊 AI 중장기 TOP10")
    df = read_csv_safe(AI_LONG_TOP10_FILE)
    if df.empty:
        st.warning("데이터 없음")
    else:
        st.dataframe(df, use_container_width=True, height=420)

with tab4:
    st.subheader("🔎 코스피 전체 AI 스캔")
    df = read_csv_safe(SCANNER_RESULT_FILE)
    if df.empty:
        st.warning("스캐너 결과 없음")
    else:
        st.dataframe(df, use_container_width=True, height=500)

st.caption("KDH AI QUANT DASHBOARD")