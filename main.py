import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="지역별 인구구조 시각화", layout="centered")

st.title("📊 지역별 연령별 인구구조 시각화")
st.write("출처: 통계청 / 2025년 5월 기준")

# 데이터 불러오기
@st.cache_data
def load_data():
    df = pd.read_csv("202505_202505_연령별인구현황_월간.csv", encoding="cp949")
    df = df.rename(columns=lambda x: x.strip())  # 열 이름 공백 제거
    return df

df = load_data()

# 시도 리스트 추출
regions = df["행정기관"].unique()
selected_region = st.selectbox("📍 지역 선택", regions)

# 선택한 지역의 데이터 필터링
region_df = df[df["행정기관"] == selected_region]

# 남성과 여성 데이터 분리 및 전처리
male_df = region_df[region_df["성별"] == "남자"]
female_df = region_df[region_df["성별"] == "여자"]

# 연령별 인구 구성
male_df["인구수"] = male_df["2025년05월_계"].str.replace(",", "").astype(int)
female_df["인구수"] = -female_df["2025년05월_계"].str.replace(",", "").astype(int)  # 음수로 변환

pop_df = pd.DataFrame({
    "연령": male_df["연령별"],
    "남자": male_df["인구수"],
    "여자": female_df["인구수"]
})

# Melt 형태로 변환 (Plotly용)
pop_df_melted = pd.melt(pop_df, id_vars="연령", var_name="성별", value_name="인구수")

# 정렬
pop_df_melted["연령"] = pd.Categorical(pop_df_melted["연령"], categories=male_df["연령별"], ordered=True)
pop_df_melted = pop_df_melted.sort_values("연령")

# 그래프 생성
fig = px.bar(
    pop_df_melted,
    y="연령",
    x="인구수",
    color="성별",
    orientation="h",
    title=f"{selected_region}의 연령별 인구 구조 (2025년 5월)",
    color_discrete_map={"남자": "blue", "여자": "red"},
    labels={"인구수": "인구 수", "연령": "연령대"}
)

fig.update_layout(
    yaxis=dict(title="연령대"),
    xaxis=dict(title="인구 수", tickformat=","),
    bargap=0.1,
    height=800
)

st.plotly_chart(fig, use_container_width=True)
