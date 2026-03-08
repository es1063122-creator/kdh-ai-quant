import os
import pandas as pd
from config import PREDICTION_LOG_FILE


def save_prediction(data):
    new_row = pd.DataFrame([data])

    if os.path.exists(PREDICTION_LOG_FILE):
        try:
            df = pd.read_csv(PREDICTION_LOG_FILE, encoding="utf-8-sig")
        except Exception:
            df = pd.read_csv(PREDICTION_LOG_FILE)
        df = pd.concat([df, new_row], ignore_index=True)
    else:
        df = new_row

    # 엑셀 한글 깨짐 방지
    df.to_csv(PREDICTION_LOG_FILE, index=False, encoding="utf-8-sig")