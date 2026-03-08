import sys
import os

# 상위 폴더 import 가능하게 설정
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import pandas as pd
import numpy as np

from data_loader import download_price


# -----------------------------
# RSI 계산
# -----------------------------
def compute_rsi(series, period=14):

    delta = series.diff()

    gain = delta.clip(lower=0).rolling(period).mean()

    loss = (-delta.clip(upper=0)).rolling(period).mean()

    rs = gain / loss.replace(0, np.nan)

    return 100 - (100 / (1 + rs))


# -----------------------------
# 매수 / 매도 타이밍 분석
# -----------------------------
def analyze_timing(name, ticker, qty, buy_price):

    # ticker 보정
    ticker = str(ticker).zfill(6)

    print("데이터 다운로드:", ticker)

    df = download_price(ticker)

    if df is None or len(df) < 60:
        print("데이터 부족:", ticker)
        return None

    df["ma5"] = df["Close"].rolling(5).mean()
    df["ma20"] = df["Close"].rolling(20).mean()

    df["ret1"] = df["Close"].pct_change()
    df["ret3"] = df["Close"].pct_change(3)

    df["rsi"] = compute_rsi(df["Close"])

    df["vol_ratio"] = df["Volume"] / df["Volume"].rolling(20).mean()

    df = df.dropna()

    if df.empty:
        return None

    last = df.iloc[-1]

    price = float(last["Close"])

    profit = (price / buy_price - 1) * 100

    score = 0

    # -----------------------------
    # 모멘텀
    # -----------------------------
    if last["ret1"] > 0:
        score += 10

    if last["ret3"] > 0:
        score += 10

    # -----------------------------
    # 이동평균
    # -----------------------------
    if price > last["ma5"]:
        score += 10

    if price > last["ma20"]:
        score += 10

    # -----------------------------
    # 거래량
    # -----------------------------
    if last["vol_ratio"] > 1.5:
        score += 15

    # -----------------------------
    # RSI
    # -----------------------------
    if last["rsi"] < 40:
        score += 10

    if last["rsi"] > 75:
        score -= 10

    # -----------------------------
    # 수익률 반영
    # -----------------------------
    if profit > 5:
        score -= 5

    if profit < -5:
        score -= 10

    # -----------------------------
    # 신호 판단
    # -----------------------------
    if score >= 40:
        signal = "추가매수 고려"

    elif score >= 20:
        signal = "보유 유지"

    elif score >= 0:
        signal = "분할매도 고려"

    else:
        signal = "손절 경고"

    return {

        "종목": name,
        "티커": ticker,
        "현재가": round(price, 2),
        "보유수량": qty,
        "매입가": buy_price,
        "수익률(%)": round(profit, 2),
        "RSI": round(last["rsi"], 2),
        "거래량배수": round(last["vol_ratio"], 2),
        "점수": score,
        "신호": signal
    }