from datetime import datetime, time, timedelta
import streamlit as st

# 1. 페이지 기본 설정
st.set_page_config(
    page_title="수면 사이클 계산기", page_icon="🌙", layout="centered"
)

# 2. 앱 제목 및 설명
st.title("🌙 수면 사이클 계산기")
st.write("나만의 수면 사이클을 찾아 개운한 취침 및 기상 시간을 계산해 드립니다!")
st.divider()

# 3. 사이드바: 1단계 (수면 사이클 확인 및 추정)
with st.sidebar:
    st.header("⚙️ 1단계: 수면 사이클 설정")

    know_cycle = st.radio(
        "본인의 수면 사이클(분)을 알고 계신가요?",
        options=["예, 알고 있습니다", "아니오, 찾아보고 싶습니다"],
    )

    st.divider()

    if know_cycle == "예, 알고 있습니다":
        sleep_cycle = st.number_input(
            "수면 사이클(분)을 입력하세요:",
            min_value=30,
            max_value=180,
            value=90,
            step=5,
        )
    else:
        st.subheader("🔍 나만의 수면 사이클 찾기")
        st.caption(
            "개운하게 잤던 총 수면 시간(n시간)을 입력하면 80, 90, 100분으로 나누어 떨어지는지 확인합니다."
        )

        sleep_hours = st.number_input(
            "평소 개운하게 잤던 수면 시간 (시간 단위):",
            min_value=1.0,
            max_value=16.0,
            value=7.5,
            step=0.5,
        )

        total_minutes = int(round(sleep_hours * 60))
        candidates = [c for c in (80, 90, 100) if total_minutes % c == 0]

        if candidates:
            st.success(
                f"총 **{total_minutes}분**은 **{candidates}분**으로 딱 나누어 떨어집니다!"
            )
            default_idx = (80, 90, 100).index(candidates[0])
        else:
            best = min(
                (80, 90, 100),
                key=lambda c: min(total_minutes % c, c - (total_minutes % c)),
            )
            st.info(
                f"총 **{total_minutes}분**은 딱 나누어 떨어지지 않지만, **{best}분** 사이클과 가장 가깝습니다."
            )
            default_idx = (80, 90, 100).index(best)

        sleep_cycle = st.selectbox(
            "적용할 수면 사이클(분)을 선택하세요:",
            options=[80, 90, 100],
            index=default_idx,
        )

    st.divider()
    st.metric(label="현재 적용된 수면 사이클", value=f"{sleep_cycle}분")

# 4. 메인 화면: 2단계 (계산 방식 및 기준 시간 입력)
st.subheader("⏰ 2단계: 기준 시간 입력")

calc_mode = st.radio(
    "어떤 시간을 기준으로 계산할까요?",
    options=[
        "기상 시간 입력 ➡️ 추천 취침 시간 계산",
        "취침 시간 입력 ➡️ 추천 기상 시간 계산",
    ],
    horizontal=True,
)

is_wake_mode = calc_mode.startswith("기상 시간")

if is_wake_mode:
    target_time = st.time_input("원하는 기상 시간을 선택하세요:", value=time(7, 0))
else:
    target_time = st.time_input(
        "예정된 취침 시간을 선택하세요:", value=time(23, 30)
    )

st.write("")

# 5. 계산 실행 버튼 및 결과 출력
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    calc_btn = st.button(
        "✨ 최적의 수면 시간 계산하기", use_container_width=True, type="primary"
    )

if calc_btn:
    base_dt = datetime.combine(datetime.today(), target_time)
    st.divider()

    if is_wake_mode:
        st.success(
            f"🌅 **{target_time.strftime('%H:%M')}**에 개운하게 일어나기 위한 추천 취침 시간입니다."
        )
    else:
        st.success(
            f"🛌 **{target_time.strftime('%H:%M')}**에 잠들었을 때 개운하게 일어날 수 있는 추천 기상 시간입니다."
        )

    # k = 3 ~ 6 사이클 계산 결과를 2x2 카드 형태로 출력
    cols = st.columns(2)
    for idx, k in enumerate(range(3, 7)):
        duration_mins = sleep_cycle * k
        hours, mins = divmod(duration_mins, 60)

        if is_wake_mode:
            result_dt = base_dt - timedelta(minutes=duration_mins)
            label = "추천 취침"
        else:
            result_dt = base_dt + timedelta(minutes=duration_mins)
            label = "추천 기상"

        # 5~6사이클 권장 배지 표시
        badge = "⭐ 권장" if k in (5, 6) else "짧은 수면"

        with cols[idx % 2]:
            st.markdown(
                f"""
                <div style="text-align: center; padding: 20px; background-color: #f0f2f6; border-radius: 15px; margin-bottom: 15px;">
                    <span style="background-color: #e0e4ec; color: #333; padding: 4px 10px; border-radius: 10px; font-size: 0.85em; font-weight: bold;">
                        {k}사이클 ({hours}시간 {mins:02d}분) · {badge}
                    </span>
                    <p style="color: #666; margin: 12px 0 4px 0; font-size: 0.95em;">{label} 시간</p>
                    <h2 style="color: #1f77b4; font-size: 2.2em; margin: 0;">🕒 {result_dt.strftime('%H:%M')}</h2>
                </div>
                """,
                unsafe_allow_html=True,
            )

# 6. 하단: 수면 사이클 계산 원리 안내 (접이식)
st.write("")
with st.expander("💡 수면 사이클 계산 원리 보기"):
    st.write(f"""
    - **수면 사이클**: 사람은 잠자는 동안 얕은 잠(렘수면)과 깊은 잠(비렘수면)을 주기적으로 반복합니다.
    - **계산 공식**: `기준 시간 ± ({sleep_cycle}분 × k회)`
    - 사이클이 끝나는 얕은 잠 단계에서 깨어나야 피로감 없이 개운하게 일어날 수 있습니다. (성인 기준 보통 **5~6사이클** 권장)
    """)
