import streamlit as st
import pandas as pd
import plotly.express as px

# 데이터 불러오기
@st.cache_data
def load_data():
    df = pd.read_csv("202505_202505_연령별인구현황_월간.csv", encoding="euc-kr")
    return df

df = load_data()

# 전처리
age_columns = [col for col in df.columns if "계_" in col and "세" in col]
age_labels = [col.split("_")[-1].replace("세", "").replace(" ", "") for col in age_columns]
df_age = df[["행정구역"] + age_columns].copy()
df_age.columns = ["행정구역"] + age_labels
df_age = df_age.melt(id_vars=["행정구역"], var_name="나이", value_name="인구수")
df_age["나이"] = df_age["나이"].str.replace("이상", "").replace("100", "100").astype(int)
df_age["인구수"] = df_age["인구수"].str.replace(",", "").astype(int)

# Streamlit UI
st.set_page_config(page_title="연령별 인구 구조 시각화", layout="wide")
st.title("📊 연령별 인구 구조 시각화")
st.markdown("#### 원하는 **동 이름**을 검색하여 인구 구조를 확인해보세요.")

# 검색창
dong_options = sorted(df_age["행정구역"].unique())
selected_dong = st.selectbox("행정구역 선택 (예: 서울특별시 종로구 사직동(1111053000))", dong_options)

# 선택된 동의 데이터 필터링
filtered_df = df_age[df_age["행정구역"] == selected_dong]

# 전체 인구수
total_population = filtered_df["인구수"].sum()
filtered_df["비율(%)"] = (filtered_df["인구수"] / total_population * 100).round(2)

# 그래프
fig = px.bar(
    filtered_df,
    x="나이",
    y="비율(%)",
    hover_data=["인구수"],
    title=f"{selected_dong}의 연령별 인구 비율 (총 인구: {total_population:,}명)",
    labels={"나이": "연령", "비율(%)": "인구 비율 (%)"},
    height=600
)
fig.update_layout(template="plotly_white")

st.plotly_chart(fig, use_container_width=True)

# 하단 정보
st.markdown("---")
st.markdown("**🔍 데이터 출처**: 통계청 월간 연령별 인구현황 CSV")
