import pandas as pd


def build_portfolio(score_df, top_n=5):

    if score_df is None or score_df.empty:
        return pd.DataFrame()

    df = score_df.head(top_n).copy()

    total_score = df["AI점수"].sum()

    if total_score == 0:
        df["비중"] = round(100 / len(df), 2)

    else:
        df["비중"] = (df["AI점수"] / total_score * 100).round(2)

    return df[["종목", "AI점수", "비중"]]


def save_portfolio(df, filename="ai_portfolio.csv"):

    if df is None or df.empty:
        return

    df.to_csv(
        filename,
        index=False,
        encoding="utf-8-sig"
    )