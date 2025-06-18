import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="🗺️ 지역별 인구 구조 대시보드", layout="wide")

@st.cache_data
def load_data() -> tuple[pd.DataFrame, list]:
    """
    CSV를 읽어 ‘지역’ 칼럼을 추가하고, 연령별 숫자 칼럼을 정수형으로 바꾼 뒤
    (age_cols, df) 형태로 리턴합니다.
    """
    df = pd.read_csv(
        "202505_202505_연령별인구현황_월간.csv",
        encoding="cp949"
    )

    # '서울특별시 (1100000000)' → '서울특별시'
    df["지역"] = df["행정구역"].str.split("(").str[0].str.strip()

    # 연령별 칼럼 자동 탐색
    age_cols = [c for c in df.columns if c.endswith("세") and "_계_" in c]

    # 천 단위 콤마 제거 후 정수형으로 변환
    for col in age_cols:
        df[col] = (
            df[col]
            .astype(str)
            .str.replace(",", "", regex=False)
            .astype(int)
        )

    return df, age_cols

# ---------- 🌐 UI ----------
st.title("🔍 지역별 인구 구조 대시보드")
df, age_cols = load_data()

regions = sorted(df["지역"].unique())
selected = st.sidebar.multiselect("✅ 분석할 지역(복수 선택 가능)", regions, default=["서울특별시"])

if not selected:
    st.info("왼쪽 사이드바에서 최소 1개 지역을 선택하세요!")
    st.stop()

chart_type = st.sidebar.selectbox(
    "차트 유형", ("꺾은선 그래프", "막대 그래프 (Population Pyramid용)")
)

# ---------- 📊 데이터 가공 ----------
subset = df[df["지역"].isin(selected)]
agg = subset.groupby("지역")[age_cols].sum().T

# 인덱스(‘…_0세’) → 숫자 추출
agg.index = agg.index.str.extract(r"(\d+)").astype(int).squeeze()
agg = agg.sort_index()  # 0, 1, ..., 100

# ---------- 🎨 시각화 ----------
if chart_type.startswith("꺾은선"):
    fig = go.Figure()
    for region in agg.columns:
        fig.add_trace(
            go.Scatter(
                x=agg.index,         # 나이
                y=agg[region],       # 인구 수
                mode='lines+markers',
                name=region
            )
        )

    fig.update_layout(
        title="연령별 인구 분포 (선 그래프)",
        xaxis_title="나이(세)",
        yaxis_title="인구 수",
        hovermode="x unified",
        height=600
    )

else:
    if len(selected) == 1:
        # 피라미드: 양쪽 대칭 막대 그래프
        pop = agg[selected[0]]
        half = len(pop) // 2
        male = pop.iloc[:half]
        female = pop.iloc[half:]
        female.index = male.index  # 같은 나이대 맞추기

        df_pyr = pd.DataFrame({
            "나이": male.index,
            "남성": male.values * -1,
            "여성": female.values
        })

        df_pyr = df_pyr.sort_values(by="나이")

        fig = go.Figure()
        fig.add_bar(x=df_pyr["남성"], y=df_pyr["나이"], name="남성", orientation="h")
        fig.add_bar(x=df_pyr["여성"], y=df_pyr["나이"], name="여성", orientation="h")

        fig.update_layout(
            title=f"{selected[0]} 인구 피라미드",
            xaxis_title="인구 수",
            yaxis_title="나이(세)",
            barmode="relative",
            height=800
        )

    else:
        # 다지역 비교용 막대 그래프
        agg_reset = agg.reset_index().rename(columns={"index": "나이"})
        fig = px.bar(
            agg_reset,
            x="나이",
            y=selected,
            barmode="group",
            labels={"value": "인구 수", "나이": "나이(세)", "variable": "지역"},
            title="연령별 인구 분포 (막대 그래프)"
        )
        fig.update_layout(
            xaxis_title="나이(세)",
            yaxis_title="인구 수",
            height=600
        )

st.plotly_chart(fig, use_container_width=True)
st.caption("데이터 출처: 행정안전부 주민등록 인구 통계")
