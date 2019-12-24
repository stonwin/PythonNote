# 패키지 임포트
import pandas as pd
import numpy as np
# 리퀘스트 모듈
import requests
## 아나콘다 설치시 BeautifulSoup 포함되어 설치.
## HTML 파싱을 위한 외부 모듈.
from bs4 import BeautifulSoup
from datetime import datetime, date, time
# ## 함수 선언

# In[ ]:
now = datetime.now()
## html 소스 내용을 받아 온다.
html = Get현재고시환율소스(now)

print('안녕하세요. Python')
print(html)
