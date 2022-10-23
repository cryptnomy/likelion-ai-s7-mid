import numpy as np
import pandas as pd
import seaborn as sns
import koreanize_matplotlib
import matplotlib.pyplot as plt
import plotly.express as px
import folium
from streamlit_folium import st_folium
import streamlit as st
import requests

# 페이지 설정
st.set_page_config(
    page_title="12걸지 마시조",
    page_icon="💢",
    initial_sidebar_state= 'expanded'
)


# 지도 생성
final_map = folium.Map(location = [37.5759,126.9768], zoom_start = 11)

# 지도 위한 데이터
df = pd.read_parquet('https://github.com/cryptnomy/likelion-ai-s7-mid/blob/master/data/hypo_2.parqeut.gzip?raw=true')

df_map = pd.DataFrame(df['충전소명'].unique()).rename(columns = {0 : '충전소명'})
df_map = pd.merge(df_map, df.groupby(['충전소명','위도','경도','급속충전기(대)','완속충전기(대)']).mean().reset_index()[['위도','경도','충전소명','급속충전기(대)','완속충전기(대)']], on ='충전소명')
df_map = pd.merge(df.groupby(['자치구','충전소명']).sum().reset_index()[['자치구','충전소명']], df_map)
df_gu_map= pd.merge(df_map.groupby('자치구')[['급속충전기(대)','완속충전기(대)']].sum().reset_index(), df_map.groupby('자치구')['충전소명'].count().reset_index())
gu_loc = """강남구 37.5172 127.0473
강동구 37.5301 127.1238
강북구 37.6398 127.0255
강서구 37.5510 126.8495
관악구 37.4781 126.9515
광진구 37.5384 127.0822
구로구 37.4955 126.8876
금천구 37.4519 126.9020
노원구 37.6543 127.0575
도봉구 37.6688 127.0471
동대문구 37.5742 127.0398
동작구 37.5124 126.9393
마포구 37.5634 126.9034
서대문구 37.5793 126.9365
서초구 37.4836 127.0327
성동구 37.5634 127.0369
성북구 37.5894 127.0167
송파구 37.5117 127.1059
양천구 37.5170 126.8666
영등포구 37.5263 126.8963
용산구 37.5323 126.9907
은평구 37.6015 126.9304
종로구 37.5735 126.9790
중구 37.5641 126.9979
중랑구 37.6063 127.0932"""
gu_df = pd.DataFrame(gu_loc.split('\n'))[0].str.split(expand = True)
gu_df.columns = ['자치구', '위도','경도']
df_gu_map = pd.merge(df_gu_map, gu_df)
geo_data = requests.get('https://raw.githubusercontent.com/cubensys/Korea_District/master/3_%EC%84%9C%EC%9A%B8%EC%8B%9C_%EC%9E%90%EC%B9%98%EA%B5%AC/%EC%84%9C%EC%9A%B8_%EC%9E%90%EC%B9%98%EA%B5%AC_%EA%B2%BD%EA%B3%84_2017.geojson').json()

ee_car = pd.read_csv('https://raw.githubusercontent.com/cryptnomy/likelion-ai-s7-mid/master/data/seoul-any-gu-ev.csv', encoding = 'cp949')
ee_car['시군구별'] = ee_car['시군구별'].str.replace('중 구', '중구')
ee_car = ee_car[ee_car['연월별'] == '2021-12-31'][['시군구별','계']]
ee_car_mount = pd.DataFrame(ee_car.groupby('시군구별')['계'].sum()).reset_index()
ee_car_mount = ee_car_mount.rename(columns = {'시군구별' : '자치구'})
ee_station = df.groupby('자치구')['충전소명'].nunique().copy()
ee_station = pd.DataFrame(ee_station).reset_index()
ee_station = ee_station.rename(columns = {'충전소명' : '충전소수'})
ee_per = pd.merge(ee_car_mount,ee_station,on='자치구')
ee_per = ee_per.rename(columns = {"계" : "자치구별 전기차 대수"})

gu_charger = df.groupby(['자치구','충전소명'])[['급속충전기(대)','완속충전기(대)']].mean().groupby('자치구').sum().reset_index()
gu_charger['총 충전기수'] = gu_charger['급속충전기(대)'] + gu_charger['완속충전기(대)']

ee_per = pd.merge(ee_per , gu_charger)
ee_per['충전기 당 전기차'] = ee_per['자치구별 전기차 대수'] / ee_per['총 충전기수']


folium.Choropleth(
    geo_data = geo_data,
    data = ee_per,
    columns = ('자치구', '충전기 당 전기차'),
    key_on="feature.properties.SIG_KOR_NM",
    fill_color = 'Blues',
    legend_name = '충전소 수',
).add_to(final_map)
from folium.plugins import MarkerCluster
mc = MarkerCluster()

for i, row in df_map.iterrows():
    
    iframe = folium.IFrame('충전소명 : '+ row['충전소명'] + '<br>' +'급속충전기 : ' + str(row['급속충전기(대)']) + '<br>' + '완속충전기 : '+ str(row['완속충전기(대)']))
    popup = folium.Popup(iframe,min_width=200, max_width=300)
    
    mc.add_child(
        folium.Marker(location = [row['위도'], row['경도']],
               popup= popup
              )
    )

mc.add_to(final_map)    
 





st.header("""💢12걸지마시조
***MID project***  
멋쟁이 사자처럼 AI SCHOOL 7기  
김지현, 박경택, 이예원, 임종우, 정의민""")
# button = st.button('시작!')
# if bool(button) : st.balloons()
'---'
st.title('***전기차 충전소는 정말로 부족한가?***')


'### 🚗커지는 전기차 시장'
"""
- 전기차 판매량은 해마다 늘어나는 추세
- 2021년에는 신규 등록이 10만대를 돌파
"""
'### ⚡가장 큰 우려 : 충전소 부족'
"""
- 전기차를 구매하는데에 다양한 우려와 고민도 존재
- 가격, 안전성, 짧은 주행거리 등 다양한 원인
- 가장 큰 우려는 '충전소 부족'
    """


'### 충전소는 진짜로 부족할까?'
with st.expander('서울특별시 내 충전기 지도로 살펴보기!') :
    st_map = st_folium(final_map)
    '배경 색상은 충전기 하나 당 담당하는 전기차 수를 의미합니다.'
st.image('https://s3.us-west-2.amazonaws.com/secure.notion-static.com/5575478b-24da-4767-98b2-4f9a77cc1053/Untitled.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=AKIAT73L2G45EIPT3X45%2F20221022%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20221022T171016Z&X-Amz-Expires=86400&X-Amz-Signature=ad0b565654a99571055aea8a10e3f337fb83aab3dbd22482adf30a9f9165093d&X-Amz-SignedHeaders=host&response-content-disposition=filename%20%3D%22Untitled.png%22&x-id=GetObject')
"""
- 서울특별시 자치구 별, 주유기 당 자동차 개수와 충전기 당 전기차 개수 비교 결과
- 주유기 한 개가 담당하는 자동차의 개수가 월등히 많다.
- 그렇다면 전기차 충전기는 정말로 부족한 것일까? 단지 우려는 아닐까?


#### 정말 부족한지 알아보고, 부족하다면 해결 방법을 생각해보자.

"""
'---'
'### 알아본 방법 1. 충전기 수와 전기차 수 비교'
"""
- 충전기 개수 당 전기차 수 파악, 부족여부 확인
- 주유기 개수 당 전기차 수 파악
- 화석연료 차와, 전기차의 충전 소요시간 및 1회 충전시 주행거리 파악
- 비교하여 전기차 충전기가 진짜 부족한 것인지 파악


"""


'### 알아본 방법 2. 시간대별 분석을 통한 상대적 파악'
"""
- 시간대 별 충전 빈도수 파악
- 시간대 별 자치구 유동인구 파악
- 시간대 별 자치구 충전 빈도수 파악
- 유동인구와 비교하여 분석
- 어느 지역에서, 어느 시간대에 부족한지 파악
- 충전이 주로 일어나는 시간대를 파악, 충전소의 수용량 및 1회 충전시 소요 시간과 비교

"""
'---'

'### 결론 : 전기차 충전소는 부족하다.'
"""
절대적인 개수로 보아도 전기차 충전소는 부족하다. 그러나 그렇게 심각한 정도는 아니다.

그러나, 긴 충전시간으로 인한 충전 가능 시간대의 제약(오전 및 오후 일과 시간 내 불가능), 이로 인한 완속충전기의 사용 증가가 충전기 부족의 더 큰 원인임을 알 수 있었다.
"""

'#### 제언'
"""
충전기 부족 문제의 가장 큰 원인이 충전 가능 시간대의 제약과 완속 충전기의 많은 사용이었다.
따라서, 충전 가능 시간대에 제약이 없도록 유동인구가 많은 상업 지역에 급속 충전기를 추가로 설치하고, 다른 곳에도 급속 충전기의 보급을 늘린다면, 충전기 부족 문제를 효율적으로 줄일 수 있을 것이다.
"""

