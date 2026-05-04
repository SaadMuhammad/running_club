import streamlit as st

from funcs.helpers import (
    init_app_state,
    get_runs_df,
    render_stat_cards,
    render_club_reward_progress,
    recent_activity,
    build_leaderboard,
    get_club_reward_status,
    get_fun_stats,
    check_app_password,
)
from funcs.styles import (
    inject_global_css,
    section_header,
    activity_card_html,
    quote_banner,
    get_random_quote,
    highlight_box,
)

st.set_page_config(page_title="Running Club Hub", page_icon="\U0001f3c3", layout="wide")
inject_global_css()
init_app_state()
check_app_password()
df = get_runs_df()

# -- Hero Header --
st.markdown(
    """
    <div style="text-align:center; padding: 1rem 0 0.5rem 0;">
        <h1 style="font-size:2.5rem; font-weight:800; margin:0;">
            \U0001f3c3 Running Club Hub
        </h1>
        <p style="color:#8B8FA3; font-size:1.05rem; margin-top:0.3rem;">
            New season. New goals. Shared progress. Shared celebration.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# -- Motivational Quote --
st.markdown(quote_banner(get_random_quote()), unsafe_allow_html=True)

# -- Stat Cards --
render_stat_cards(df)

# -- Club Reward Progress --
render_club_reward_progress(df, title="Club Reward Countdown")

# -- Celebration trigger --
club_status = get_club_reward_status(df)
if club_status["goal_runs"] > 0:
    if club_status["progress_runs"] >= club_status["goal_runs"]:
        if not st.session_state.get("celebrated_club_meal"):
            st.snow()
            st.session_state["celebrated_club_meal"] = True

# -- Two-column: Activity Feed + Quick Highlights --
left, right = st.columns([1.3, 1])

with left:
    st.markdown(section_header("Recent Activity"), unsafe_allow_html=True)
    activity_df = recent_activity(df)
    if activity_df.empty:
        st.info("No activity yet. Add entries from the Admin page.")
    else:
        cards_html = ""
        for _, row in activity_df.iterrows():
            cards_html += activity_card_html(
                runner=row["Runner"],
                date=row["Date"],
                distance=row["Distance (km)"],
                run_type=row["Run Type"],
                notes=row.get("Notes", ""),
            )
        st.markdown(cards_html, unsafe_allow_html=True)

with right:
    st.markdown(section_header("Quick Highlights"), unsafe_allow_html=True)

    if df.empty:
        st.info("No data yet. Add entries from the Admin page.")
    else:
        board = build_leaderboard(df)
        top_runner = board.iloc[0]["Runner"]
        top_runs = int(board.iloc[0]["Runs"])

        st.markdown(
            highlight_box(
                f"\U0001f451 Top runner: <strong>{top_runner}</strong> with <strong>{top_runs} runs</strong>"
            ),
            unsafe_allow_html=True,
        )
        st.markdown(
            highlight_box(
                f"\U0001f4cf Total club distance: <strong>{df['distance_km'].sum():.1f} km</strong>",
                "orange",
            ),
            unsafe_allow_html=True,
        )
        st.markdown(
            highlight_box(
                f"\U0001f37d\ufe0f Club meals unlocked: <strong>{club_status['club_rewards']}</strong>"
            ),
            unsafe_allow_html=True,
        )

    # -- Fun Facts --
    st.markdown(section_header("Fun Facts"), unsafe_allow_html=True)
    fun = get_fun_stats(df)
    if fun:
        st.markdown(
            f"\U0001f3df\ufe0f You've covered **{fun['football_pitches']:.0f}** football pitches worth of distance!"
        )
        st.markdown(
            f"\U0001f5fc That's **{fun['eiffel_towers']:.0f}** Eiffel Towers laid end to end!"
        )
        st.markdown(f"\U0001f4c5 Most popular run day: **{fun['most_active_day']}**")
    else:
        st.caption("Fun facts will appear once runs are logged.")
