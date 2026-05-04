from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


DEFAULT_DATA_PATH = "assets/running.csv"
RUNS_PER_REWARD = 4


def check_app_password():
    """Gate the app behind a password. Call at the top of every page."""
    if st.session_state.get("app_authenticated"):
        return

    app_pw = st.secrets.get("APP_PASSWORD", "runclub2026")
    st.markdown(
        '<h2 style="text-align:center; margin-top:3rem;">🔒 Running Club Hub</h2>'
        '<p style="text-align:center; color:#8B8FA3;">Enter the app password to continue.</p>',
        unsafe_allow_html=True,
    )
    password = st.text_input("Password", type="password", key="app_pw_input")
    if st.button("Login"):
        if password == app_pw:
            st.session_state["app_authenticated"] = True
            st.rerun()
        else:
            st.error("Incorrect password.")
    st.stop()

REQUIRED_COLUMNS = [
    "runner_name",
    "date",
    "distance_km",
    "run_type",
    "notes",
]


def init_app_state():
    if "data_path" not in st.session_state:
        st.session_state["data_path"] = DEFAULT_DATA_PATH

    if "admin_ok" not in st.session_state:
        st.session_state["admin_ok"] = False

    if "runs_df" not in st.session_state:
        st.session_state["runs_df"] = load_data(st.session_state["data_path"])


def clean_runs_df(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    for col in REQUIRED_COLUMNS:
        if col not in df.columns:
            df[col] = None

    if df.empty:
        return df

    df["runner_name"] = df["runner_name"].fillna("").astype(str).str.strip()
    df["run_type"] = df["run_type"].fillna("Easy Run").astype(str)
    df["notes"] = df["notes"].fillna("").astype(str)
    df["distance_km"] = pd.to_numeric(df["distance_km"], errors="coerce").fillna(0.0)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    df = df.dropna(subset=["date"])
    df = df[df["runner_name"] != ""]

    df["date_only"] = df["date"].dt.date
    df["year_week"] = df["date"].dt.strftime("%Y-W%U")
    df["month"] = df["date"].dt.strftime("%Y-%m")

    df = df.sort_values("date", ascending=False).reset_index(drop=True)
    return df


def load_data(data_path: str) -> pd.DataFrame:
    path = Path(data_path)

    if path.exists():
        df = pd.read_csv(path)
    else:
        df = pd.DataFrame(columns=REQUIRED_COLUMNS)

    return clean_runs_df(df)


def save_data(df: pd.DataFrame, data_path: str):
    path = Path(data_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    save_df = df.copy()
    for col in ["date_only", "year_week", "month"]:
        if col in save_df.columns:
            save_df = save_df.drop(columns=[col])

    save_df.to_csv(path, index=False)


def refresh_data():
    st.session_state["runs_df"] = load_data(st.session_state["data_path"])
    for key in list(st.session_state.keys()):
        if key.startswith("celebrated_"):
            del st.session_state[key]


def get_runs_df() -> pd.DataFrame:
    return st.session_state["runs_df"].copy()


def set_runs_df(df: pd.DataFrame):
    st.session_state["runs_df"] = clean_runs_df(df)


def get_runner_summary(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=["runner_name", "runs", "distance_km"])

    summary = (
        df.groupby("runner_name", as_index=False)
        .agg(
            runs=("runner_name", "size"),
            distance_km=("distance_km", "sum"),
        )
        .sort_values(["runs", "distance_km"], ascending=[False, False])
        .reset_index(drop=True)
    )
    return summary


# ==========================================================
# Individual reward logic
# ==========================================================
def individual_reward_number(total_runs: int) -> int:
    return total_runs // RUNS_PER_REWARD


def individual_runs_to_next_reward(total_runs: int) -> int:
    if total_runs == 0:
        return RUNS_PER_REWARD

    remainder = total_runs % RUNS_PER_REWARD
    if remainder == 0:
        return 0
    return RUNS_PER_REWARD - remainder


def individual_reward_progress(total_runs: int):
    if total_runs == 0:
        return 0, RUNS_PER_REWARD

    current = total_runs % RUNS_PER_REWARD
    if current == 0:
        current = RUNS_PER_REWARD

    return current, RUNS_PER_REWARD


# ==========================================================
# Club reward logic
# Rule:
# Club meal unlocks only when ALL unique participants
# complete the same 4-run block.
# Example:
# - first club meal => everyone has at least 4 runs
# - second club meal => everyone has at least 8 runs
# ==========================================================
def get_club_reward_status(df: pd.DataFrame) -> dict:
    summary = get_runner_summary(df)

    if summary.empty:
        return {
            "total_people": 0,
            "club_rewards": 0,
            "next_target_per_person": RUNS_PER_REWARD,
            "completed_people_for_next_target": 0,
            "progress_runs": 0,
            "goal_runs": 0,
            "remaining_runs": 0,
        }

    total_people = len(summary)

    # How many full 4-run blocks every runner has completed
    club_rewards = int((summary["runs"] // RUNS_PER_REWARD).min())

    lower_threshold = club_rewards * RUNS_PER_REWARD
    next_target_per_person = lower_threshold + RUNS_PER_REWARD

    progress_per_runner = (summary["runs"] - lower_threshold).clip(lower=0, upper=RUNS_PER_REWARD)
    progress_runs = int(progress_per_runner.sum())
    goal_runs = int(total_people * RUNS_PER_REWARD)
    remaining_runs = int(goal_runs - progress_runs)

    completed_people_for_next_target = int((summary["runs"] >= next_target_per_person).sum())

    return {
        "total_people": total_people,
        "club_rewards": club_rewards,
        "next_target_per_person": next_target_per_person,
        "completed_people_for_next_target": completed_people_for_next_target,
        "progress_runs": progress_runs,
        "goal_runs": goal_runs,
        "remaining_runs": remaining_runs,
    }


# ==========================================================
# Badges
# ==========================================================
ALL_INDIVIDUAL_BADGES = [
    {"text": "\U0001f3c1 First Run", "run_req": 1, "dist_req": 0, "hint": "Complete your first run"},
    {"text": "\U0001f37d\ufe0f First Personal Meal", "run_req": 4, "dist_req": 0, "hint": "Reach 4 runs"},
    {"text": "\U0001f525 Double Meal Unlock", "run_req": 8, "dist_req": 0, "hint": "Reach 8 runs"},
    {"text": "\U0001f3c5 Consistency Champ", "run_req": 12, "dist_req": 0, "hint": "Reach 12 runs"},
    {"text": "\U0001f680 Four-Block Finisher", "run_req": 16, "dist_req": 0, "hint": "Reach 16 runs"},
    {"text": "\U0001f4cf 25K Club", "run_req": 0, "dist_req": 25, "hint": "Run 25 km total distance"},
    {"text": "\U0001f31f 50K Club", "run_req": 0, "dist_req": 50, "hint": "Run 50 km total distance"},
]


def assign_individual_badges(total_runs: int, total_distance: float) -> list[str]:
    badges = []

    if total_runs >= 1:
        badges.append("\U0001f3c1 First Run")
    if total_runs >= 4:
        badges.append("\U0001f37d\ufe0f First Personal Meal")
    if total_runs >= 8:
        badges.append("\U0001f525 Double Meal Unlock")
    if total_runs >= 12:
        badges.append("\U0001f3c5 Consistency Champ")
    if total_runs >= 16:
        badges.append("\U0001f680 Four-Block Finisher")
    if total_distance >= 25:
        badges.append("\U0001f4cf 25K Club")
    if total_distance >= 50:
        badges.append("\U0001f31f 50K Club")

    return badges


def get_all_individual_badges(total_runs: int, total_distance: float) -> list[dict]:
    """Return all badges with earned/locked status and unlock hint."""
    result = []
    for b in ALL_INDIVIDUAL_BADGES:
        earned = True
        if b["run_req"] > 0 and total_runs < b["run_req"]:
            earned = False
        if b["dist_req"] > 0 and total_distance < b["dist_req"]:
            earned = False
        result.append({"text": b["text"], "earned": earned, "hint": b["hint"]})
    return result


def assign_club_badges(df: pd.DataFrame) -> list[str]:
    summary = get_runner_summary(df)
    if summary.empty:
        return []

    badges = []
    total_people = len(summary)

    at_4 = int((summary["runs"] >= 4).sum())
    at_8 = int((summary["runs"] >= 8).sum())
    at_12 = int((summary["runs"] >= 12).sum())

    club_status = get_club_reward_status(df)
    club_rewards = club_status["club_rewards"]

    if at_4 >= 3:
        badges.append("🤝 Trio Starter — 3 runners reached 4 runs")
    if at_4 >= 5:
        badges.append("🍽️ Feast Squad — 5 runners reached 4 runs")
    if at_8 >= 3:
        badges.append("🚀 Endurance Trio — 3 runners reached 8 runs")
    if at_8 >= 5:
        badges.append("🔥 Power Pack — 5 runners reached 8 runs")
    if at_12 >= 3:
        badges.append("🏅 Iron Trio — 3 runners reached 12 runs")

    if total_people >= 3 and at_4 == total_people:
        badges.append("🎉 Everyone to Four")
    if total_people >= 3 and at_8 == total_people:
        badges.append("🏆 Everyone to Eight")
    if total_people >= 3 and at_12 == total_people:
        badges.append("👑 Everyone to Twelve")

    if club_rewards >= 1:
        badges.append("🍽️ First Club Feast Unlocked")
    if club_rewards >= 2:
        badges.append("🍽️🍽️ Second Club Feast Unlocked")
    if club_rewards >= 3:
        badges.append("🌈 Third Club Feast Unlocked")

    return badges


ALL_CLUB_BADGES = [
    {"text": "🤝 Trio Starter", "hint": "3 runners reach 4 runs"},
    {"text": "🍽️ Feast Squad", "hint": "5 runners reach 4 runs"},
    {"text": "🚀 Endurance Trio", "hint": "3 runners reach 8 runs"},
    {"text": "🔥 Power Pack", "hint": "5 runners reach 8 runs"},
    {"text": "🏅 Iron Trio", "hint": "3 runners reach 12 runs"},
    {"text": "🎉 Everyone to Four", "hint": "All runners (min 3) reach 4 runs"},
    {"text": "🏆 Everyone to Eight", "hint": "All runners (min 3) reach 8 runs"},
    {"text": "👑 Everyone to Twelve", "hint": "All runners (min 3) reach 12 runs"},
    {"text": "🍽️ First Club Feast Unlocked", "hint": "Unlock 1 club meal reward"},
    {"text": "🍽️🍽️ Second Club Feast Unlocked", "hint": "Unlock 2 club meal rewards"},
    {"text": "🌈 Third Club Feast Unlocked", "hint": "Unlock 3 club meal rewards"},
]


def get_all_club_badges(df: pd.DataFrame) -> list[dict]:
    """Return all club badges with earned/locked status and unlock hints."""
    summary = get_runner_summary(df)
    if summary.empty:
        total_people = 0
        at_4 = at_8 = at_12 = 0
        club_rewards = 0
    else:
        total_people = len(summary)
        at_4 = int((summary["runs"] >= 4).sum())
        at_8 = int((summary["runs"] >= 8).sum())
        at_12 = int((summary["runs"] >= 12).sum())
        club_rewards = get_club_reward_status(df)["club_rewards"]

    earned_checks = [
        at_4 >= 3,
        at_4 >= 5,
        at_8 >= 3,
        at_8 >= 5,
        at_12 >= 3,
        total_people >= 3 and at_4 == total_people,
        total_people >= 3 and at_8 == total_people,
        total_people >= 3 and at_12 == total_people,
        club_rewards >= 1,
        club_rewards >= 2,
        club_rewards >= 3,
    ]

    result = []
    for badge_def, is_earned in zip(ALL_CLUB_BADGES, earned_checks):
        result.append({
            "text": badge_def["text"],
            "earned": is_earned,
            "hint": badge_def["hint"],
        })
    return result


def build_leaderboard(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=["Rank", "Runner", "Runs", "Distance (km)", "Badges"])

    board = get_runner_summary(df).copy()
    board["Rank"] = board.index + 1
    board["Badges"] = board.apply(
        lambda row: " | ".join(
            assign_individual_badges(int(row["runs"]), float(row["distance_km"]))
        ) or "-",
        axis=1,
    )

    board = board.rename(
        columns={
            "runner_name": "Runner",
            "runs": "Runs",
            "distance_km": "Distance (km)",
        }
    )

    board["Distance (km)"] = board["Distance (km)"].round(2)

    return board[["Rank", "Runner", "Runs", "Distance (km)", "Badges"]]


def recent_activity(df: pd.DataFrame, limit: int = 8) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=["Date", "Runner", "Distance (km)", "Run Type", "Notes"])

    out = df[["date", "runner_name", "distance_km", "run_type", "notes"]].copy().head(limit)
    out["date"] = out["date"].dt.strftime("%Y-%m-%d")

    out = out.rename(
        columns={
            "date": "Date",
            "runner_name": "Runner",
            "distance_km": "Distance (km)",
            "run_type": "Run Type",
            "notes": "Notes",
        }
    )
    return out


def render_stat_cards(df: pd.DataFrame):
    from funcs.styles import stat_cards_row

    total_runs = int(len(df))
    total_distance = float(df["distance_km"].sum()) if not df.empty else 0.0
    active_runners = int(df["runner_name"].nunique()) if not df.empty else 0
    club_rewards = get_club_reward_status(df)["club_rewards"]

    cards = [
        {"icon": "\U0001f3c3", "value": str(total_runs), "label": "Total Runs", "color": "orange"},
        {"icon": "\U0001f4cf", "value": f"{total_distance:.1f}", "label": "Total Distance (km)", "color": "blue"},
        {"icon": "\U0001f465", "value": str(active_runners), "label": "Active Runners", "color": "green"},
        {"icon": "\U0001f37d\ufe0f", "value": str(club_rewards), "label": "Club Meals Unlocked", "color": "purple"},
    ]
    st.markdown(stat_cards_row(cards), unsafe_allow_html=True)


def render_club_reward_progress(df: pd.DataFrame, title: str = "Next Club Meal Progress"):
    from funcs.styles import section_header, custom_progress_bar, highlight_box

    status = get_club_reward_status(df)

    st.markdown(section_header(title), unsafe_allow_html=True)

    if status["total_people"] == 0:
        st.markdown(
            highlight_box(
                "No runs logged yet. The first club meal unlocks when all participants reach 4 runs.",
                "orange",
            ),
            unsafe_allow_html=True,
        )
        return

    progress_value = status["progress_runs"] / status["goal_runs"] if status["goal_runs"] else 0
    label = f"{status['progress_runs']}/{status['goal_runs']} runs"
    st.markdown(custom_progress_bar(progress_value, label), unsafe_allow_html=True)

    st.markdown(
        highlight_box(
            f"<strong>{status['completed_people_for_next_target']} / {status['total_people']}</strong> runners "
            f"have reached <strong>{status['next_target_per_person']} runs</strong>. "
            f"{status['remaining_runs']} more runner-runs needed for the next club meal."
        ),
        unsafe_allow_html=True,
    )


def render_badges(badges: list[str], title: str = "Badges", empty_message: str = "No badges yet."):
    from funcs.styles import section_header, badge_pills_html

    st.markdown(section_header(title), unsafe_allow_html=True)
    st.markdown(badge_pills_html(badges), unsafe_allow_html=True)


def render_badges_with_progress(
    all_badges: list[dict], title: str = "Badges"
):
    """Render all badges showing earned (colored) and locked (grayscale)."""
    from funcs.styles import section_header, badge_pills_with_progress_html

    st.markdown(section_header(title), unsafe_allow_html=True)
    st.markdown(badge_pills_with_progress_html(all_badges), unsafe_allow_html=True)


def plot_weekly_runs(df: pd.DataFrame):
    if df.empty:
        return None

    weekly = (
        df.groupby("year_week", as_index=False)
        .agg(runs=("runner_name", "size"))
        .sort_values("year_week")
    )

    fig = px.line(
        weekly,
        x="year_week",
        y="runs",
        markers=True,
        title="Weekly Runs Trend",
    )
    fig.update_layout(xaxis_title="Week", yaxis_title="Runs")
    return apply_chart_theme(fig)


def plot_runner_distances(df: pd.DataFrame):
    if df.empty:
        return None

    by_runner = (
        df.groupby("runner_name", as_index=False)
        .agg(distance_km=("distance_km", "sum"))
        .sort_values("distance_km", ascending=False)
    )

    fig = px.bar(
        by_runner,
        x="runner_name",
        y="distance_km",
        title="Distance by Runner",
    )
    fig.update_layout(xaxis_title="Runner", yaxis_title="Distance (km)")
    return apply_chart_theme(fig)


def plot_monthly_runs(df: pd.DataFrame):
    if df.empty:
        return None

    monthly = (
        df.groupby("month", as_index=False)
        .agg(runs=("runner_name", "size"))
        .sort_values("month")
    )

    fig = px.bar(
        monthly,
        x="month",
        y="runs",
        title="Monthly Runs",
    )
    fig.update_layout(xaxis_title="Month", yaxis_title="Runs")
    return apply_chart_theme(fig)


def add_manual_entry(
    df: pd.DataFrame,
    runner_name: str,
    run_date,
    distance_km: float,
    run_type: str,
    notes: str,
) -> pd.DataFrame:
    new_row = pd.DataFrame(
        [
            {
                "runner_name": runner_name.strip(),
                "date": pd.to_datetime(run_date),
                "distance_km": distance_km,
                "run_type": run_type,
                "notes": notes.strip(),
            }
        ]
    )
    updated = pd.concat([df, new_row], ignore_index=True)
    return clean_runs_df(updated)

def plot_cumulative_runner_distance(df: pd.DataFrame):
    if df.empty:
        return None

    race_df = df.copy()
    race_df = race_df.sort_values(["runner_name", "date"])

    race_df["cum_distance_km"] = race_df.groupby("runner_name")["distance_km"].cumsum()

    fig = px.line(
        race_df,
        x="date",
        y="cum_distance_km",
        color="runner_name",
        markers=True,
        title="Cumulative KM Race",
    )

    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Cumulative Distance (km)",
        legend_title="Runner",
    )
    return apply_chart_theme(fig)

def plot_runner_race(df: pd.DataFrame):
    if df.empty:
        return None

    race_df = (
        df.groupby("runner_name", as_index=False)
        .agg(distance_km=("distance_km", "sum"))
        .sort_values("distance_km", ascending=False)
        .reset_index(drop=True)
    )

    race_df["rank"] = race_df.index + 1
    max_distance = float(race_df["distance_km"].max())
    x_max = max_distance * 1.12 if max_distance > 0 else 1

    def get_medal_color(rank: int) -> str:
        if rank == 1:
            return "gold"
        if rank == 2:
            return "silver"
        if rank == 3:
            return "#cd7f32"  # bronze
        return "#4c78a8"

    fig = go.Figure()

    # tighter race tracks
    for _, row in race_df.iterrows():
        fig.add_trace(
            go.Scatter(
                x=[0, max_distance],
                y=[row["runner_name"], row["runner_name"]],
                mode="lines",
                line=dict(width=10, color="rgba(180,180,180,0.35)"),
                showlegend=False,
                hoverinfo="skip",
            )
        )

    # progress markers one by one so top 3 can have different colors
    for _, row in race_df.iterrows():
        runner = row["runner_name"]
        distance = float(row["distance_km"])
        rank = int(row["rank"])

        label = f"{distance:.1f} km"
        if rank == 1:
            label = f"👑 {label}"

        fig.add_trace(
            go.Scatter(
                x=[distance],
                y=[runner],
                mode="markers+text",
                text=[label],
                textposition="middle right",
                marker=dict(
                    size=24 if rank == 1 else 20,
                    color=get_medal_color(rank),
                    line=dict(width=2, color="white"),
                ),
                name=runner,
                showlegend=False,
                hovertemplate=f"<b>{runner}</b><br>Rank: #{rank}<br>Distance: {distance:.1f} km<extra></extra>",
            )
        )

    fig.update_layout(
        title="Race Track View",
        xaxis_title="Distance Covered (km)",
        yaxis_title="",
        xaxis=dict(
            range=[0, x_max],
            showgrid=True,
            gridcolor="rgba(255,255,255,0.08)",
            zeroline=False,
        ),
        yaxis=dict(
            categoryorder="array",
            categoryarray=race_df["runner_name"].tolist()[::-1],  # leader at top
            showgrid=False,
        ),
        height=max(380, len(race_df) * 62),
        plot_bgcolor="rgba(26,29,41,0.8)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color="#FAFAFA"),
        title_font=dict(size=18, color="#FAFAFA"),
        margin=dict(l=40, r=80, t=60, b=40),
    )

    return fig


# ==========================================================
# Chart theming
# ==========================================================
def apply_chart_theme(fig):
    from funcs.styles import PLOTLY_COLORS

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(26,29,41,0.8)",
        font=dict(family="Inter, sans-serif", color="#FAFAFA"),
        title_font=dict(size=18, color="#FAFAFA"),
        colorway=PLOTLY_COLORS,
        xaxis=dict(gridcolor="rgba(255,255,255,0.08)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.08)"),
        margin=dict(l=40, r=40, t=60, b=40),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(color="#C8CADE"),
        ),
    )
    return fig


# ==========================================================
# Streak calculation
# ==========================================================
def calculate_weekly_streak(df: pd.DataFrame, runner_name: str) -> int:
    runner_df = df[df["runner_name"] == runner_name].copy()
    if runner_df.empty:
        return 0

    runner_df["week_start"] = runner_df["date"].dt.to_period("W").apply(
        lambda p: p.start_time
    )
    active_weeks = sorted(runner_df["week_start"].unique(), reverse=True)

    if len(active_weeks) == 0:
        return 0

    streak = 1
    for i in range(1, len(active_weeks)):
        diff = (active_weeks[i - 1] - active_weeks[i]).days
        if diff <= 7:
            streak += 1
        else:
            break
    return streak


# ==========================================================
# Fun stats
# ==========================================================
def get_fun_stats(df: pd.DataFrame) -> dict:
    if df.empty:
        return {}

    total_km = df["distance_km"].sum()
    stats = {
        "total_km": total_km,
        "football_pitches": total_km * 1000 / 105,
        "eiffel_towers": total_km * 1000 / 330,
        "avg_distance": df["distance_km"].mean(),
        "longest_run": df["distance_km"].max(),
        "longest_runner": df.loc[df["distance_km"].idxmax(), "runner_name"],
        "most_active_day": df["date"].dt.day_name().mode().iloc[0],
    }
    return stats