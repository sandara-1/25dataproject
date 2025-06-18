import streamlit as st
import pandas as pd
import plotly.express as px

# 📌 페이지 설정
st.set_page_config(page_title="인구 피라미드 시각화", layout="centered")
st.title("📊 지역별 인구구조 시각화")
st.caption("출처: 통계청 | 2025년 5월 기준")

# ✅ 데이터 로딩 함수
@st.cache_data
def load_data():
    df = pd.read_csv("202505_202505_연령별인구현황_월간.csv", encoding="cp949")
    df.columns = df.columns.str.strip()  # 열 이름 공백 제거
    return df

df = load_data()

# ✅ 열 이름 출력 (초기 디버깅용)
st.write("ℹ️ 데이터 열 이름:", df.columns.tolist())

# ✅ 필수 열 자동 감지
try:
    col_region = [col for col in df.columns if "행정" in col or "지역" in col or "시도" in col][0]
    col_gender = [col for col in df.columns if "성별" in col][0]
    col_age = [col for col in df.columns if "연령" in col][0]
    col_value = df.columns[-1]  # 가장 마지막 열 = 인구 수
except IndexError:
    st.error("❌ 필요한 열(행정기관, 성별, 연령별, 인구 수)을 찾을 수 없습니다.")
    st.stop()

# ✅ 사용자 입력: 지역 선택
regions = df[col_region].unique()
selected_region = st.selectbox("📍 지역을 선택하세요", regions)

# ✅ 선택한 지역 데이터 필터링
region_df = df[df[col_region] == selected_region]

# ✅ 남녀 분리
male_df = region_df[region_df[col_gender] == "남자"].copy()
female_df = region_df[region_df[col_gender] == "여자"].copy()

# ✅ 인구수 숫자 처리
male_df["인구수"] = male_df[col_value].astype(str).str.replace(",", "").astype(int)
female_df["인구수"] = female_df[col_value].astype(str).str.replace(",", "").astype(int) * -1  # 음수로 변경

# ✅ 연령별 통합
pop_df = pd.DataFrame({
    "연령": male_df[col_age].values,
    "남자": male_df["인구수"].values,
    "여자": female_df["인구수"].values
})

# ✅ Plotly 시각화를 위한 long-form 데이터
pop_long = pop_df.melt(id_vars="연령", var_name="성별", value_name="인구수")
pop_long["연령"] = pd.Categorical(pop_long["연령"], categories=male_df[col_age].tolist(), ordered=True)
pop_long = pop_long.sort_values("연령")

# ✅ Plotly 그래프
fig = px.bar(
    pop_long,
    y="연령",
    x="인구수",
    color="성별",
    orientation="h",
    color_discrete_map={"남자": "royalblue", "여자": "salmon"},
    title=f"{selected_region}의 연령별 인구구조 (2025년 5월)"
)
fig.update_layout(
    xaxis_title="인구 수",
    yaxis_title="연령대",
    height=800,
    xaxis_tickformat=","
)

# ✅ 그래프 출력
st.plotly_chart(fig, use_container_width=True)
