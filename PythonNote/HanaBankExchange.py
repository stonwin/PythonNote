# 패키지 임포트
import pandas as pd
import numpy as np
# 리퀘스트 모듈
import requests
## 아나콘다 설치시 BeautifulSoup 포함되어 설치.
## HTML 파싱을 위한 외부 모듈.
from bs4 import BeautifulSoup
from datetime import datetime, date, time

## 함수
def 데이터추출(rows):
    ## 행을 담을 리스트 선언
    rlst = []
    for row in rows:
        ## 값을 담을 리스트
        values = []
        for itag in row:
            if itag.name == "th" or itag.name == "td":
                values.append(itag.text.strip())
        rlst.append(values)
    return rlst


## 문자를 숫자데이터로 변환 하는 함수.
def 숫자변환(ser):    
    try:
        if ser.name == "통화명":
            return ser
        # "," 제거
        ser = ser.str.replace(",", "")
        # 상승, 하락 변환
        ser = ser.str.replace("상승", "+").str.replace("하락", "-").str.replace(" ", "")
        # 등락율 처리
        ser = ser.str.replace("%", "")
        # 데이터 타입 변경
        ser = ser.map(float)
        return ser
    except:
        # 예외가 발생하면... 그냥 시리즈 리턴.
        return ser



def Get현재고시환율소스(now):
    retDate = '{0.year}-{0.month:02d}-{0.day:02d}'.format(now)
    # print(retDate)
    # ajax=true, curCd=, tmpInqStrDt=2019-05-31, pbldDvCd=3, pbldSqn=, hid_key_data=, inqStrDt=20190531, inqKindCd=1, hid_enc_data=, requestTarget=searchContentDiv
    url = "https://www.kebhana.com/cms/rate/wpfxd651_01i_01.do"
    ## post 데이터 설정.
    postData = dict(ajax="true", curCd="", tmpInqStrDt=retDate, 
                    pbldDvCd="3", pbldSqn="", 
                    hid_key_data="", 
                    inqStrDt='{0.year}{0.month:02d}{0.day:02d}'.format(now), 
                    inqKindCd="1", hid_enc_data="", requestTarget="searchContentDiv")
    res = requests.post(url, data=postData)
    ## 인코딩.
    res.encoding = "utf-8"

    ## html 소스 내용을 받아 온다. 
    return res.text

  
def 환율데이터추출(html):    
    # 파싱 준비
    soup = BeautifulSoup(html, "lxml")

    ## 환율 테이블의 css=tblBasic css를 이용해 가져오기.
    tbls = soup.select(".tblBasic")

    if len(tbls) == 1:
        rate_tbl = tbls[0]
        thRows = rate_tbl.thead.select("th")
        rateRows = rate_tbl.tbody.select("tr")
    thTags = pd.DataFrame(thRows)

    # 해더 부분의 칼럼명 추출... : 사용안함. 
    cols = thTags.applymap(lambda x: x.text)

    ## 데이터 추출 : 데이터추출 함수 호출 한다. 
    rateFrame = pd.DataFrame(데이터추출(rateRows))

    # 칼럼명 설정.
    rateFrame.columns = ["통화", "현찰살때환율", "현찰살때Spread", "현찰팔때환율", "현찰팔때Spread",
                         "송금보낼때", "송금받을때", "TC살때", "외화수표팔때", "매매기준율", "환가료율", "미화환산율" ]

    # 필요없는 칼럼 제거
    rateFrame = rateFrame.drop(['현찰살때Spread','현찰팔때Spread'], axis=1)

    # 통화명, 통화코드 분리, 통화 칼럼 제거
    rateFrame["통화코드"] = rateFrame['통화'].str.split(' ').str[1]
    rateFrame["통화명"] = rateFrame['통화'].str.split(' ').str[0]
    rateFrame.drop(["통화"], axis=1)

    # 인덱스 설정 
    rateFrame = rateFrame.set_index("통화코드")

    # 칼럼 다시 정렬.
    rateCols = ["통화명", "현찰살때환율", "현찰팔때환율",
                         "송금보낼때", "송금받을때", "TC살때", "외화수표팔때", "매매기준율", "환가료율", "미화환산율" ]

    rateFrame = pd.DataFrame(rateFrame, columns=rateCols)


    ## 숫자 변환 
    #rateFrame = pd.merge(rateFrame["통화명"].reset_index(), rateFrame[rateCols[1:]].apply(숫자변환).reset_index())

    rateFrame = rateFrame.apply(숫자변환)
    return rateFrame  


def Get고시회차(html):
    ## 고시회차 정보 css=fl
    soup = BeautifulSoup(html, "lxml")
    rateInfo = soup.select(".fl")
    #rateInfo.select("strong")
    rinfo = pd.Series(rateInfo[0].select("strong"))
    rinfo = rinfo.map(lambda tag : tag.text)
    return rinfo


## 크롤링 실행 및 저장 
## 하나은행 접속 
## 현재 환율 조회 URL https://www.kebhana.com/cms/rate/wpfxd651_01i_01.do
## 하나은행의 화율은 post 방식으로 요청
## body Form 컬렉션 전송

## 오늘 일자.
now = datetime.now()

## html 소스 내용을 받아 온다. 
html = Get현재고시환율소스(now)

## 고시회차 정보 css=fl
rateInfo = Get고시회차(html)

## 환율 추출
rateDF = 환율데이터추출(html)

## 크롤링된 환율 데이터 출력
print(rateInfo[0], rateInfo[2], rateInfo[1])
print(rateDF)

# 데이터 저장. 
# saveFileName = '환율{0}_{1}.xlsx'.format('{0.year}-{0.month:02d}-{0.day:02d}'.format(now),  rateInfo[1])
# rateDF.to_excel(saveFileName)