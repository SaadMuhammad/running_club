import streamlit as st

from funcs.helpers import (
    init_app_state,
    get_runs_df,
    render_stat_cards,
    render_club_reward_progress,
    get_all_club_badges,
    render_badges_with_progress,
    plot_weekly_runs,
    plot_runner_distances,
    plot_monthly_runs,
    plot_runner_race,
    get_club_reward_status,
    check_app_password,
)
from funcs.styles import (
    inject_global_css,
    stat_cards_row,
    section_header,
)

init_app_state()
check_app_password()
df = get_runs_df()

inject_global_css()

st.markdown(
    '<h1 style="font-size:2rem; font-weight:800;">'
    "\U0001f3c5 Running Club Progress Hub</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    '<p style="color:#8B8FA3;">Club-wide trends, milestones, badges, and memories.</p>',
    unsafe_allow_html=True,
)

# -- Stat Cards --
render_stat_cards(df)

# -- Club Reward Progress --
render_club_reward_progress(df)

# -- Club Status Cards --
club_status = get_club_reward_status(df)
extra_cards = [
    {
        "icon": "\U0001f37d\ufe0f",
        "value": str(club_status["club_rewards"]),
        "label": "Club Meal Rewards",
        "color": "purple",
    },
    {
        "icon": "\U0001f465",
        "value": f"{club_status['completed_people_for_next_target']}/{club_status['total_people']}",
        "label": "Runners at Next Target",
        "color": "teal",
    },
    {
        "icon": "\U0001f3af",
        "value": str(club_status["next_target_per_person"]),
        "label": "Next Target Per Runner",
        "color": "yellow",
    },
]
st.markdown(stat_cards_row(extra_cards), unsafe_allow_html=True)

# -- Race Track Chart --
st.markdown(section_header("Race Track View"), unsafe_allow_html=True)
race_fig = plot_runner_race(df)
if race_fig is not None:
    st.plotly_chart(race_fig, use_container_width=True)
else:
    st.info("Runner race chart will appear after data is added.")

# -- Club Badges --
all_club_badges = get_all_club_badges(df)
render_badges_with_progress(all_club_badges, title="Club Badges")

# -- Charts --
col1, col2 = st.columns(2)

with col1:
    weekly_fig = plot_weekly_runs(df)
    if weekly_fig is not None:
        st.plotly_chart(weekly_fig, use_container_width=True)
    else:
        st.info("Weekly trend will appear after data is added.")

with col2:
    distance_fig = plot_runner_distances(df)
    if distance_fig is not None:
        st.plotly_chart(distance_fig, use_container_width=True)
    else:
        st.info("Runner distance chart will appear after data is added.")

monthly_fig = plot_monthly_runs(df)
if monthly_fig is not None:
    st.plotly_chart(monthly_fig, use_container_width=True)

# -- Photo Memory Section --
st.markdown(section_header("Photo Memories"), unsafe_allow_html=True)
st.caption("Upload run photos, celebration meal photos, and club memories.")

photos = st.file_uploader(
    "Upload photos for preview",
    type=["png", "jpg", "jpeg"],
    accept_multiple_files=True,
)

if photos:
    cols = st.columns(min(3, len(photos)))
    for i, photo in enumerate(photos):
        cols[i % len(cols)].image(photo, caption=photo.name, use_container_width=True)
else:
    st.info("No photos uploaded yet.")
