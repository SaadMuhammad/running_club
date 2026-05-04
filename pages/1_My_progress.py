import streamlit as st
import plotly.express as px

from funcs.helpers import (
    init_app_state,
    get_runs_df,
    build_leaderboard,
    individual_reward_number,
    individual_runs_to_next_reward,
    individual_reward_progress,
    get_all_individual_badges,
    render_badges_with_progress,
    calculate_weekly_streak,
    apply_chart_theme,
    check_app_password,
)
from funcs.styles import (
    inject_global_css,
    stat_cards_row,
    section_header,
    custom_progress_bar,
    streak_display,
    highlight_box,
)

init_app_state()
check_app_password()
df = get_runs_df()

inject_global_css()

st.markdown(
    '<h1 style="font-size:2rem; font-weight:800;">\U0001f4c8 My Progress</h1>',
    unsafe_allow_html=True,
)

# -- Leaderboard --
st.markdown(section_header("Leaderboard"), unsafe_allow_html=True)
leaderboard = build_leaderboard(df)
st.dataframe(leaderboard, use_container_width=True, hide_index=True)

# -- Runner Selector --
st.markdown(section_header("Runner View"), unsafe_allow_html=True)

runners = sorted(df["runner_name"].dropna().unique().tolist()) if not df.empty else []

if not runners:
    st.warning("No runner data available yet.")
    st.stop()

selected_runner = st.selectbox(
    "Choose a runner",
    runners,
    key="my_progress_runner_select",
)

# -- Balloons on runner switch --
previous_runner = st.session_state.get("last_selected_runner_for_progress")
if previous_runner is not None and previous_runner != selected_runner:
    st.balloons()
st.session_state["last_selected_runner_for_progress"] = selected_runner

runner_df = df[df["runner_name"] == selected_runner].copy()

total_runs = int(len(runner_df))
total_distance = float(runner_df["distance_km"].sum())
meal_milestones = individual_reward_number(total_runs)
next_goal = individual_runs_to_next_reward(total_runs)
all_badges = get_all_individual_badges(total_runs, total_distance)
streak = calculate_weekly_streak(df, selected_runner)

# -- Streak Display --
st.markdown(streak_display(streak), unsafe_allow_html=True)

# -- Styled Stat Cards --
cards = [
    {"icon": "\U0001f3c3", "value": str(total_runs), "label": "Runs", "color": "orange"},
    {"icon": "\U0001f4cf", "value": f"{total_distance:.1f}", "label": "Distance (km)", "color": "blue"},
    {"icon": "\U0001f37d\ufe0f", "value": str(meal_milestones), "label": "Personal Meals", "color": "green"},
    {"icon": "\U0001f3af", "value": str(next_goal), "label": "Runs to Next Meal", "color": "red"},
]
st.markdown(stat_cards_row(cards), unsafe_allow_html=True)

# -- Celebration on reward block completion --
current, goal = individual_reward_progress(total_runs)
if current == goal and total_runs > 0:
    session_key = f"celebrated_{selected_runner}_{meal_milestones}"
    if not st.session_state.get(session_key):
        st.balloons()
        st.session_state[session_key] = True

st.caption(
    "Personal meal rewards unlock individually. "
    "Club meals unlock only when everyone completes the same 4-run block."
)

# -- Badges (earned + locked) --
render_badges_with_progress(all_badges, title="Personal Badges")

# -- Two columns: Run History + Progress --
left, right = st.columns([1.2, 1])

with left:
    st.markdown(
        section_header(f"{selected_runner}'s Run History"), unsafe_allow_html=True
    )

    show_df = runner_df[["date", "distance_km", "run_type", "notes"]].copy()
    show_df["date"] = show_df["date"].dt.strftime("%Y-%m-%d")
    show_df = show_df.rename(
        columns={
            "date": "Date",
            "distance_km": "Distance (km)",
            "run_type": "Run Type",
            "notes": "Notes",
        }
    )

    st.dataframe(show_df, use_container_width=True, hide_index=True)

with right:
    st.markdown(
        section_header("Progress to Next Personal Reward"), unsafe_allow_html=True
    )
    label = f"{current}/{goal} runs"
    st.markdown(
        custom_progress_bar(current / goal if goal else 0, label),
        unsafe_allow_html=True,
    )

    if total_runs == 0:
        st.caption("This runner has not logged a run yet.")
    elif current == goal:
        st.markdown(
            highlight_box("Personal meal reward block completed!"),
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            highlight_box(
                f"{goal - current} more run(s) to complete this personal reward block.",
                "orange",
            ),
            unsafe_allow_html=True,
        )

    trend_df = (
        runner_df.groupby("month", as_index=False)
        .agg(distance_km=("distance_km", "sum"))
        .sort_values("month")
    )

    if not trend_df.empty:
        fig = px.bar(
            trend_df,
            x="month",
            y="distance_km",
            title=f"{selected_runner} Monthly Distance",
        )
        fig.update_layout(xaxis_title="Month", yaxis_title="Distance (km)")
        fig = apply_chart_theme(fig)
        st.plotly_chart(fig, use_container_width=True)
