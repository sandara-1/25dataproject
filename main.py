import streamlit as st
import pandas as pd
import plotly.express as px

# 데이터 불러오기
@st.cache_data
def load_data():
    df = pd.read_csv("202505_202505_연령별인구현황_월간.csv", encoding="euc-kr")
    return df

df = load_data()

# 나이 열 가공
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

# UI 구성
st.set_page_config(page_title="행정동 인구 비교 시각화", layout="wide")
st.title("📊 행정동 연령별 인구수시각화")
st.markdown("두 개의 행정동을 선택하여 인구 비율을 비교하거나, 하나만 선택하여 단독 확인할 수 있습니다.")

# 좌우 컬럼
col1, col2 = st.columns([1, 3])

with col1:
    st.subheader("🏙️ 행정동 선택")

    dong_options = ["없음"] + sorted(df_age["행정구역"].unique())
    selected_dong1 = st.selectbox("➊ 첫 번째 행정동", dong_options, key="dong1")
    selected_dong2 = st.selectbox("➋ 두 번째 행정동", dong_options, key="dong2")

    selected_age = st.slider("🎚️ 특정 나이 선택 (인구 확인)", 0, 100, 30)

    st.markdown("### 👶 선택 나이 인구수")
    for dong in [selected_dong1, selected_dong2]:
        if dong != "없음":
            pop = df_age[(df_age["행정구역"] == dong) & (df_age["나이"] == selected_age)]["인구수"]
            if not pop.empty:
                st.markdown(f"- `{dong}`의 {selected_age}세 인구수: **{pop.values[0]:,}명**")
            else:
                st.markdown(f"- `{dong}`의 {selected_age}세 인구 데이터 없음")

with col2:
    valid_dongs = [dong for dong in [selected_dong1, selected_dong2] if dong != "없음"]

    if len(valid_dongs) == 0:
        st.warning("⛔ 최소한 하나의 행정동을 선택해주세요.")
    
    elif len(valid_dongs) == 1:
        dong = valid_dongs[0]
        single_df = df_age[df_age["행정구역"] == dong].copy()
        total_pop = single_df["인구수"].sum()

        fig = px.bar(
            single_df,
            x="나이",
            y="인구수",
            title=f"{dong}의 연령별 인구수 (총 인구: {total_pop:,}명)",
            labels={"나이": "연령", "인구수": "인구수 (명)"},
            height=600,
        )
        fig.update_layout(template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)

    else:
        compare_df = df_age[df_age["행정구역"].isin(valid_dongs)].copy()

        fig = px.bar(
            compare_df,
            x="나이",
            y="인구수",
            color="행정구역",
            barmode="group",
            title=f"{valid_dongs[0]} vs {valid_dongs[1]} 연령별 인구수 비교",
            labels={"나이": "연령", "인구수": "인구수 (명)"},
            height=600,
        )
        fig.update_layout(template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)


# 하단 정보
st.markdown("---")
st.markdown("**📂 데이터 출처**: 통계청 월간 연령별 인구현황 CSV")
