import pandas as pd


# -----------------------------
# AI 점수 계산
# -----------------------------
def calculate_ai_score(prob, accuracy, recent_return, flow):

    score = (
        prob * 0.4 +
        accuracy * 0.3 +
        recent_return * 0.1 +
        flow * 0.2
    )

    return round(score * 100, 2)


# -----------------------------
# 점수 테이블 생성
# -----------------------------
def build_score_table(results):

    rows = []

    for r in results:

        prob = r.get("단타확률", 0) / 100
        acc = r.get("단타정확도", 0) / 100
        recent_return = r.get("최근수익률", 0)
        flow = r.get("수급", 0)

        score = calculate_ai_score(
            prob,
            acc,
            recent_return,
            flow
        )

        rows.append({
            "종목": r.get("종목"),
            "AI점수": score,
            "상승확률": r.get("단타확률", 0),
            "정확도": r.get("단타정확도", 0),
            "외국인수급": flow
        })

    df = pd.DataFrame(rows)

    if df.empty:
        return df

    df = df.sort_values("AI점수", ascending=False)
    df = df.reset_index(drop=True)

    return df