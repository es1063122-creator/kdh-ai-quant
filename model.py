import pandas as pd
import numpy as np

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split


# -----------------------------
# 특징 생성
# -----------------------------
def create_features(df):

    df = df.copy()

    df["return1"] = df["Close"].pct_change(1)
    df["return5"] = df["Close"].pct_change(5)
    df["return20"] = df["Close"].pct_change(20)

    df["ma5"] = df["Close"].rolling(5).mean()
    df["ma20"] = df["Close"].rolling(20).mean()

    df["ma_ratio"] = df["ma5"] / df["ma20"]

    df = df.dropna()

    return df


# -----------------------------
# 목표값 생성
# -----------------------------
def create_target(df, hold_days):

    df = df.copy()

    df["future"] = df["Close"].shift(-hold_days)

    df["target"] = (df["future"] > df["Close"]).astype(int)

    df = df.dropna()

    return df


# -----------------------------
# AI 학습 + 예측
# -----------------------------
def train_predict(name, ticker, stock, market, hold_days):

    if stock is None or stock.empty:
        return 0.5, 0

    df = stock.copy()

    # 특징 생성
    df = create_features(df)

    # 목표값 생성
    df = create_target(df, hold_days)

    if len(df) < 50:
        return 0.5, 0

    features = [
        "return1",
        "return5",
        "return20",
        "ma_ratio"
    ]

    X = df[features]

    y = df["target"]

    if len(X) < 20:
        return 0.5, 0

    # 학습 / 테스트 분리
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.3,
        shuffle=False
    )

    # 모델 생성
    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=10,
        random_state=42
    )

    # 학습
    model.fit(X_train, y_train)

    # 백테스트 정확도
    accuracy = model.score(X_test, y_test)

    # 마지막 데이터 예측
    last_row = X.iloc[[-1]]

    prob = model.predict_proba(last_row)[0][1]

    return prob, accuracy