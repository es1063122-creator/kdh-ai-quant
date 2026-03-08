from pykrx import stock
import pandas as pd
import datetime


def get_foreign_flow(ticker):

    try:

        end = datetime.datetime.today()
        start = end - datetime.timedelta(days=30)

        df = stock.get_market_trading_value_by_date(
            start.strftime("%Y%m%d"),
            end.strftime("%Y%m%d"),
            ticker
        )

        if df is None or df.empty:
            return 0

        foreign = df["외국인"].sum()

        if foreign > 0:
            return 1

        if foreign < 0:
            return -1

        return 0

    except Exception as e:

        print("수급 데이터 오류:", ticker, e)

        return 0