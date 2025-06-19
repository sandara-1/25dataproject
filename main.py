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
st.set_page_config(page_title="행정동 인구 비교 시각화", layout="wide")
st.title("📊 행정동 간 연령별 인구 구조 비교")
st.markdown("**두 개의 행정동을 선택하면 연령별 인구 비율을 비교할 수 있습니다.**")

# 좌우 컬럼 분할
col1, col2 = st.columns([1, 3])

with col1:
    st.subheader("🏙️ 행정동 선택")
    dong_options = sorted(df_age["행정구역"].unique())
    selected_dongs = st.multiselect(
        "비교할 행정동 2개를 선택하세요",
        dong_options,
        max_selections=2
    )

    age_check = st.slider("특정 나이 선택 (인구 확인용)", 0, 100, 30)

    if len(selected_dongs) == 2:
        st.markdown("### 👶 선택한 나이의 인구 수")
        for dong in selected_dongs:
            pop = df_age[(df_age["행정구역"] == dong) & (df_age["나이"] == age_check)]["인구수"]
            if not pop.empty:
                st.markdown(f"- `{dong}`의 {age_check}세 인구수: **{pop.values[0]:,}명**")
            else:
                st.markdown(f"- `{dong}`의 {age_check}세 인구 데이터 없음")

with col2:
    if len(selected_dongs) != 2:
        st.warning("⛔ 행정동을 **정확히 2개** 선택해주세요.")
    else:
        # 두 행정동 필터링
        comp_df = df_age[df_age["행정구역"].isin(selected_dongs)].copy()
        total_pop_by_dong = comp_df.groupby("행정구역")["인구수"].transform("sum")
        comp_df["비율(%)"] = (comp_df["인구수"] / total_pop_by_dong * 100).round(2)

        fig = px.bar(
            comp_df,
            x="나이",
            y="비율(%)",
            color="행정구역",
            barmode="group",
            title=f"{selected_dongs[0]} vs {selected_dongs[1]} 연령별 인구 비율 비교",
            labels={"나이": "연령", "비율(%)": "인구 비율 (%)"},
            height=600
        )
        fig.update_layout(template="plotly_white")

        st.plotly_chart(fig, use_container_width=True)

# 하단 정보
st.markdown("---")
st.markdown("**📂 데이터 출처**: 통계청 월간 연령별 인구현황 CSV")
