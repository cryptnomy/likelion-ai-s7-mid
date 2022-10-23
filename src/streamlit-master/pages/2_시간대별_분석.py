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
import plotly.graph_objects as go
from plotly.subplots import make_subplots



st.set_page_config(
    page_title="유동인구와 충전 데이터 비교",
    page_icon="👨‍👩‍👧‍👦",
    initial_sidebar_state= 'expanded'
)


st.write('# ⚡시간대별 충전 빈도수 분석⚡')


# 데이터 읽기

df_1 = pd.read_csv('https://raw.githubusercontent.com/cryptnomy/likelion-ai-s7-mid/master/data/hypo_1_pre.csv')
df_2 = pd.read_parquet('https://github.com/cryptnomy/likelion-ai-s7-mid/blob/master/data/hypo_2.parqeut.gzip?raw=true')

# 데이터 프레임 처리
time_list = [x for x in range(24)]
df_2 = df_2.rename(columns = {str(x) : x for x in range(24)})


# 전체 자치구 시간대별 충전 수
time_count = pd.DataFrame(df_2[time_list].sum()).reset_index().rename(columns = {'index' : '시간대', 0 : '충전수'})
# 시각화
fig0 = plt.figure(figsize = (8,4))
sns.barplot(data = time_count, x='시간대', y='충전수', ci = None, estimator = sum)
plt.ylabel('충전수')
plt.title('시간대별 충전수')
st.pyplot(fig0)

"""
시간대별 전기차 충전소의 사용 횟수를 분석해보았더니, 

**17시 부터 02시**까지의 충전 빈도수가 가장 높고, **04시 부터 09시** 까지는 충전 빈도가 적다.

##### -> 충전하는데 시간이 오래 걸리므로, 퇴근 후에 전기자동차를 충전하는 사람들의 비율이 높음을 알 수 있다.
##### 또한, 같은 이유로 새벽 및 오전 시간대에는 충전을 할 수 없는 경우가 많아, 충전 가능한 시간대가 한정되어 충전기 부족 문제가 심각해질 것으로 예상된다.
    """


# 완속 급속 충전수

fig = make_subplots(rows=1, cols=1, shared_xaxes=True)
fig.add_trace(go.Bar(x=time_list,y=df_2.groupby('충전구분')[time_list].sum().T.reset_index()['완속'],
              name='완속충전수'))
fig.add_trace(go.Bar(x=time_list,y=df_2.groupby('충전구분')[time_list].sum().T.reset_index()['급속'],
              name='급속충전수'))

fig.update_layout(
    title_text= f"시간대별 급속 및 완속 충전 빈도수"
)

fig.update_xaxes(title_text="시간대")
fig.update_yaxes(title_text="<b>충전 수</b>")


st.plotly_chart(fig)

"""
- **완속**충전 : 오전 및 일과 시간엔 사용량이 적고, 저녁 및 야간시간대에 증가

- **급속**충전 : 야간의 사용량이 매우 적고, 일과시간 중에 사용량이 가장 많음

- 분석
**급속** 충전기의 경우 80%까지 충전하는데 30분 정도로 시간이 적게 들고, 쇼핑몰, 공공기관 등 시내에 설치되어 있는 경우가 많아 **일과 시간 중 잠시 충전**하는 경우가 많을 것이다.  
**완속** 충전기의 경우 충전 시간도 4 ~ 5시간으로 오래걸리고, 주로 아파트의 주차장과 같이 일과 후 충전이 가능한 곳에 존재하여 **퇴근 후 저녁 및 야간 시간대에 충전**하는 경우가 많다고 이해할 수 있다.

-> 완속충전기의 개수와 사용 빈도수가 급속충전기에 비해 많으므로, 퇴근 후 충전하는 사람들의 비율이 높다는 앞의 분석 결과와 상통하며, 해당 시간대 충전기가 부족할 것임을 예측할 수 있다.

#### 따라서, 저녁 및 야간에 충전기가 부족할 것이다.

---


"""






# 그래프 그리기 위한 변수 처리


data_gu_time = df_1.iloc[:, [1, 4, 5]].groupby(['자치구', '시간대구분']).mean().reset_index()
data_gu_time = data_gu_time.rename(columns = {'시간대구분' : '시간대'})

data_gu_unique = data_gu_time['자치구'].unique()

gu_time = pd.DataFrame(df_2.pivot_table(index = '자치구', values = time_list, aggfunc = 'sum').stack())
gu_time = gu_time.reset_index().rename(columns = {'level_1' : '시간대'})
gu_time = gu_time.rename(columns={0:"충전빈도수"})
compare_time = pd.merge(data_gu_time, gu_time)
gu_list = compare_time['자치구'].unique().tolist()







## 구현할 것:
# 거주지역과 산업지역 구분하여 리스트 만들고, 거주지 산업지 그래프 각각 그려주기

gu_not_home = ['강남구','금천구','마포구','서대문구','서초구','영등포구','성동구','용산구','종로구','중구']
gu_home = ['강동구', '강북구', '강서구', '관악구' ,'광진구', '구로구','노원구', '도봉구', '동대문구' ,'동작구', '성북구', '송파구', '양천구',  '은평구', '중랑구']


st.write('# 👨‍👩‍👧‍👦생활인구와 ⚡충전 빈도수 비교')

"""
시간별 생활인구 수와 충전기의 사용 빈도수를 비교하여 앞에서의 분석을 뒷받침 한다.

이를 위해 먼저 회사 등이 밀집해있는 상업지역과 아파트 등이 밀집해있는 주거지역의 생활 인구 및 충전 빈도수의 특징을 알아본다.
"""


st.markdown('## 상업 및 주거지역 비교')

# 비교 그래프
plt.style.use('seaborn-paper')
# print(plt.style.available)
fig, axes = plt.subplots(1,2, figsize = (8,3))
axes2 = axes.copy()

y11 = compare_time[compare_time['자치구'] == '서초구'][['시간대','충전빈도수']]['충전빈도수']
y12 = compare_time[compare_time['자치구'] == '서초구'][['시간대','20세 이상 생활인구수']]['20세 이상 생활인구수']

axes[0].set_xlabel('시간대')
axes[0].bar(time_list, y11, color = '#FF8B8B',label='충전빈도')
axes[0].legend(loc='best')
axes[0].set_title('상업지역')


axes2[0] = axes[0].twinx()
axes2[0].plot(time_list, y12, color = '#167C80',label='생활인구', linewidth = '5')
axes2[0].legend(loc='lower left')
plt.gca().axes.yaxis.set_visible(False)

y21 = compare_time[compare_time['자치구'] == '강서구'][['시간대','충전빈도수']]['충전빈도수']
y22 = compare_time[compare_time['자치구'] == '강서구'][['시간대','20세 이상 생활인구수']]['20세 이상 생활인구수']


axes[1].bar(time_list, y21, color = '#FF8B8B',label='충전빈도')
axes[1].legend(loc='lower right')
axes[1].set_title('주거지역')
axes[1].set_xlabel('시간대')


axes2[1] = axes[1].twinx()

axes2[1].plot(time_list, y22, color = '#167C80',label='생활인구', linewidth = '5')
axes2[1].legend(loc='lower left')
plt.gca().axes.yaxis.set_visible(False)

plt.tight_layout()
st.pyplot(fig)
with st.expander('전체 자치구 시각화 결과보기'):
    st.image('https://github.com/imngooh/streamlit/raw/master/gu_time_popul_charge.png')
    
"""
서울시 모든 자치구를 시각화하여 분석한 결과, 상업지역과 주거지역이 명확히 나누어지는 모습을 보였다. 그 중 대표적인 두 곳의 그래프를 비교해보자.
"""
\
    
# 상업지역 및 주거지역 비교
st.markdown('#### 상업지역')
"""
- 생활인구 : **오전 및 오후** 시간대에 **많음**, **야간** 시간대에 **적음**  
- 충전빈도수 : **오전 및 오후** 시간대에 **적음**, **야간** 시간대에 **많음**
"""

st.markdown('#### 주거지역')
"""
- 생활인구 : **오전 및 오후** 시간대에 **적음**, **야간** 시간대에 **많음**  
- 충전빈도수 : **오전 및 오후** 시간대에 **적음**, **야간** 시간대에 **많음**
"""

st.markdown('### 결론')
"""
> 생활인구가 야간시간대에 많은 주거지역의 경우 예상대로 야간 시간대 충전 빈도가 많았다.  그런데, 생활인구가 야간시간대에 적은 상업지역조차도 야간 시간대 충전 빈도가 많았다.  
>
> 결국, 어느 지역에서든 사람들이 퇴근 후 야간 시간대에 충전을 하는 경우가 많다는 것을 알아내었다. 그렇다면, 거주지 밀집 지역에서는 야간시간대에 충전 수요가 폭발적으로 증가할 것이다.


우리는 이를 토대로,
### 거주지 밀집 지역에서 저녁 및 야간 시간대에 전기차 충전소가 부족하다.
라는 결론을 낼 수 있다.

---

앞서 자치구별로 분석한 '충전기 하나당 담당 전기차 수'와 함께 살펴보자. 
완속 충전기의 80% 충전시까지 걸리는 시간은 평균적으로 4시간 가량이다.
따라서 퇴근 시간 이후 충전이 활발한 시간대인 17시 ~ 02시 (9시간)동안, 충전기 한대당 채 두대밖에 못한다.  

따라서 완속충전기만 생각했을때, 차량이 3일에 한번씩만 충전한다고 하더라도, 충전기 한개 당 담당하는 전기차 수가 8이 넘지 않아야 충전기가 부족하지 않다고 볼 수 있다.

그러나, 모든 자치구가 8이 넘는 수치를 지녔다. 최소 수치인 도봉구조차 충전기 한 개당 9대의 전기차를 담당해야한다. 해당 수치를 보아, 다음을 확정지을 수 있다.

## 전기차 충전소는 모든 차량을 담당하기에 부족하다.

#### 이는 절대적인 개수의 문제이기도 하지만, 긴 충전시간으로 인한 충전 가능 시간대의 제약, 이로 인한 완속충전기의 사용 증가가 더 큰 원인임을 알 수 있었다.

---

    """


st.markdown('### 자치구별 생활인구 - 충전수 그래프 확인하기')
st.markdown('자치구를 선택하세요!')
st.markdown('')
# 선택지 만들기

selected_gu = st.selectbox('name', list(df_1['자치구'].unique()))
if bool(selected_gu):
    selected_data = df_1[df_1['자치구'] == selected_gu]
selected_gu_time = compare_time[compare_time['자치구'] == selected_gu].set_index('시간대')
# 선택한 구 그리고, 주거지역인지 상업지역인지 표시
# plotly 도전

fig = make_subplots(rows=1, cols=1, shared_xaxes=True,specs=[[{"secondary_y": True}]])
fig.add_trace(go.Bar(x=selected_gu_time.reset_index()['시간대'],y=selected_gu_time.reset_index()['충전빈도수'],
              name='충전수'))
fig.add_trace(go.Scatter(x=selected_gu_time.reset_index()['시간대'],y=selected_gu_time.reset_index()['20세 이상 생활인구수'],
              name='유동인구수', line = {'width' : 5}),secondary_y = True)

fig.update_layout(
    title_text= f"<b>{selected_gu}<b> 시간대별 충전 빈도수 및 유동인구 수"
)

fig.update_xaxes(title_text="시간대")
fig.update_yaxes(title_text="<b>충전 수</b>", secondary_y=False)
fig.update_yaxes(title_text="<b>생활인구 수</b>", secondary_y=True)


st.plotly_chart(fig)

locat = '주거지역' if selected_gu in gu_home else '상업지역'
st.markdown(f'**{selected_gu}**는 **{locat}**입니다.')
if locat =='주거지역' :
    st.markdown('**오전 및 오후** 시간대에 생활인구가 **적고**, **야간** 시간대에 **많습니다.**')
    st.markdown(' 충전 빈도 역시 **오전 및 오후** 시간대에 **적고**, **야간** 시간대에 **많습니다.**')
else :
    st.markdown('**오전 및 오후** 시간대에 생활인구가 **많고**, **야간** 시간대에 **적습니다.**')
    st.markdown('그러나 충전 빈도는 **오전 및 오후** 시간대에 **적고**, **야간** 시간대에 **많습니다.**')
    
    
    
    
# st.balloons()
# st.snow()