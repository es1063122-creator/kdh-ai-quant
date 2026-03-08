import pandas as pd

def generate_signal(stock):

    ma5 = stock["Close"].rolling(5).mean().iloc[-1]
    ma20 = stock["Close"].rolling(20).mean().iloc[-1]

    if ma5 > ma20:
        return "BUY"
    elif ma5 < ma20:
        return "SELL"
    else:
        return "WAIT"