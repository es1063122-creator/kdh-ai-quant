import pandas as pd
import requests
from io import BytesIO

url = "https://kind.krx.co.kr/corpgeneral/corpList.do?method=download"

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(url, headers=headers)

df = pd.read_html(BytesIO(response.content), header=0)[0]

df = df[["회사명","종목코드"]]

df["종목코드"] = df["종목코드"].astype(str).str.zfill(6)

df.to_excel("korea_stock_list.xlsx", index=False)

print("총 종목수:", len(df))
print("엑셀 생성 완료")