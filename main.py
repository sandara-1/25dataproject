import streamlit as st
import pandas as pd
import plotly.express as px

# 데이터 불러오기
@st.cache_data
def load_data():
    df = pd.read_csv("202505_202505_연령별인구현황_월간.csv", encoding="euc-kr")
    return df

df = load_data()

# 나이 관련 열 추출
age_columns = [col for col in df.columns if "계_" in col and "세" in col]
age_labels = [col.split("_")[-1].replace("세", "").replace(" ", "") for col in age_columns]

df_age = df[["행정구역"] + age_columns].copy()
df_age.columns = ["행정구역"] + age_labels
df_age = df_age.melt(id_vars=["행정구역"], var_name="나이", value_name="인구수")

# 데이터 정제
df_age["나이"] = df_age["나이"].replace("100이상", "100")
df_age["나이"] = pd.to_numeric(df_age["나이"], errors="coerce")
df_age["인구수"] = df_age["인구수"].astype(str).str.replace(",", "", regex=False)
df_age["인구수"] = pd.to_numeric(df_age["인구수"], errors="coerce")

df_age = df_age.dropna(subset=["나이", "인구수"])
df_age["나이"] = df_age["나이"].astype(int)
df_age["인구수"] = df_age["인구수"].astype(int)

# 페이지 설정
st.set_page_config(page_title="연령별 인구 구조 시각화", layout="wide")
st.title("📊 연령별 인구 구조 시각화")
st.markdown("**행정동과 나이를 선택하면 인구 비율과 해당 나이의 인구수를 확인할 수 있습니다.**")

# 좌우 컬럼 분할
col1, col2 = st.columns([1, 3])

with col1:
    st.subheader("🔍 행정동 및 나이 선택")

    dong_options = sorted(df_age["행정구역"].unique())
    selected_dong = st.selectbox("행정구역을 선택하세요", dong_options)

    selected_age = st.slider("나이를 선택하세요", min_value=0, max_value=100, value=30)

    # 선택된 행정동과 나이의 인구수 추출
    pop = df_age[(df_age["행정구역"] == selected_dong) & (df_age["나이"] == selected_age)]["인구수"]

    if not pop.empty:
        st.markdown(f"📌 **{selected_dong}의 {selected_age}세 인구수:** `{pop.values[0]:,}명`")
    else:
        st.markdown("⚠️ 선택한 나이에 대한 인구 데이터가 없습니다.")

with col2:
    filtered_df = df_age[df_age["행정구역"] == selected_dong]
    total_population = filtered_df["인구수"].sum()
    filtered_df["비율(%)"] = (filtered_df["인구수"] / total_population * 100).round(2)

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
st.markdown("**📂 데이터 출처**: 통계청 월간 연령별 인구현황 CSV")
