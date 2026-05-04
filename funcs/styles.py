"""
Centralized CSS injection and HTML component templates.
Every page calls inject_global_css() once at the top.
"""

import random

import streamlit as st

# -- Color Palette -----------------------------------------------------------
COLORS = {
    "orange": "#FF6B35",
    "blue": "#1B98E0",
    "green": "#06D6A0",
    "purple": "#7B2D8E",
    "red": "#EF476F",
    "yellow": "#FFD166",
    "teal": "#0CB4CE",
    "dark_bg": "#0F1117",
    "card_bg": "#1A1D29",
    "card_border": "#2A2D39",
    "text_primary": "#FAFAFA",
    "text_muted": "#8B8FA3",
}

PLOTLY_COLORS = [
    "#FF6B35",
    "#1B98E0",
    "#06D6A0",
    "#7B2D8E",
    "#EF476F",
    "#FFD166",
    "#0CB4CE",
    "#F77F00",
    "#4CC9F0",
    "#F72585",
]

MOTIVATIONAL_QUOTES = [
    "The miracle isn't that I finished. It's that I had the courage to start. -- John Bingham",
    "Run when you can, walk if you have to, crawl if you must; just never give up. -- Dean Karnazes",
    "Every run is a fresh start.",
    "Your only limit is you.",
    "The body achieves what the mind believes.",
    "It does not matter how slowly you go as long as you do not stop. -- Confucius",
    "Today's run is tomorrow's strength.",
    "Lace up. Show up. Never give up.",
    "You don't have to be fast. You just have to go.",
    "One run can change your day. Many runs can change your life.",
]

FUN_FACTS = [
    "The average person takes about 2,000 steps per mile of running.",
    "Running can add up to 3 years to your life expectancy.",
    "A human can outrun a horse in a marathon-distance race.",
    "Your heart pumps about 5 liters of blood per minute at rest, and up to 25 while running.",
    "Running was the only event in the first Olympic Games in 776 BC.",
    "The word 'marathon' comes from the legend of Pheidippides running 26 miles from Marathon to Athens.",
]


def get_random_quote() -> str:
    return random.choice(MOTIVATIONAL_QUOTES)


def get_random_fun_fact() -> str:
    return random.choice(FUN_FACTS)


# -- Global CSS --------------------------------------------------------------

_GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.block-container {
    padding-top: 2rem !important;
}

/* -- Stat Card Grid ------------------------------------------------------ */
.stat-card-row {
    display: flex;
    gap: 1rem;
    flex-wrap: wrap;
    margin-bottom: 1.5rem;
}

.stat-card {
    flex: 1;
    min-width: 180px;
    background: linear-gradient(135deg, var(--card-color) 0%, var(--card-color-dark) 100%);
    border-radius: 16px;
    padding: 1.25rem 1.5rem;
    color: #FAFAFA;
    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
    position: relative;
    overflow: hidden;
}

.stat-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 30px rgba(0,0,0,0.5);
}

.stat-card .card-icon { font-size: 2.2rem; margin-bottom: 0.3rem; }
.stat-card .card-value { font-size: 2rem; font-weight: 800; line-height: 1.1; }
.stat-card .card-label { font-size: 0.85rem; font-weight: 500; opacity: 0.85; margin-top: 0.25rem; }

.stat-card::after {
    content: '';
    position: absolute;
    width: 120px; height: 120px;
    border-radius: 50%;
    background: rgba(255,255,255,0.06);
    top: -30px; right: -30px;
}

.stat-card.orange  { --card-color: #FF6B35; --card-color-dark: #D4520F; }
.stat-card.blue    { --card-color: #1B98E0; --card-color-dark: #1272A8; }
.stat-card.green   { --card-color: #06D6A0; --card-color-dark: #04A578; }
.stat-card.purple  { --card-color: #7B2D8E; --card-color-dark: #5A1F68; }
.stat-card.red     { --card-color: #EF476F; --card-color-dark: #C42D52; }
.stat-card.teal    { --card-color: #0CB4CE; --card-color-dark: #088A9E; }
.stat-card.yellow  { --card-color: #F7B32B; --card-color-dark: #D49A1E; }

/* -- Badge Pills --------------------------------------------------------- */
.badge-container {
    display: flex;
    flex-wrap: wrap;
    gap: 0.75rem;
    margin: 0.75rem 0;
}

.badge-pill {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.65rem 1.4rem;
    border-radius: 999px;
    font-size: 1rem;
    font-weight: 600;
    background: rgba(255, 107, 53, 0.15);
    border: 1px solid rgba(255, 107, 53, 0.3);
    color: #FF6B35;
    transition: background 0.2s ease, transform 0.15s ease;
}

.badge-pill:hover {
    background: rgba(255, 107, 53, 0.25);
    transform: scale(1.05);
}

.badge-pill.green  { background: rgba(6, 214, 160, 0.15); border-color: rgba(6, 214, 160, 0.3); color: #06D6A0; }
.badge-pill.blue   { background: rgba(27, 152, 224, 0.15); border-color: rgba(27, 152, 224, 0.3); color: #1B98E0; }
.badge-pill.purple { background: rgba(123, 45, 142, 0.15); border-color: rgba(123, 45, 142, 0.3); color: #B06CC8; }
.badge-pill.yellow { background: rgba(255, 209, 102, 0.15); border-color: rgba(255, 209, 102, 0.3); color: #FFD166; }
.badge-pill.red    { background: rgba(239, 71, 111, 0.15); border-color: rgba(239, 71, 111, 0.3); color: #EF476F; }

.badge-pill.locked {
    background: rgba(255, 255, 255, 0.06);
    border: 1px dashed rgba(255, 255, 255, 0.25);
    color: rgba(255, 255, 255, 0.35);
    filter: grayscale(80%);
    opacity: 0.7;
    position: relative;
    cursor: default;
}

.badge-pill.locked:hover {
    background: rgba(255, 255, 255, 0.12);
    opacity: 1;
    filter: grayscale(50%);
    transform: none;
}

/* Tooltip for locked badges */
.badge-pill.locked .badge-tooltip {
    visibility: hidden;
    opacity: 0;
    position: absolute;
    bottom: calc(100% + 8px);
    left: 50%;
    transform: translateX(-50%);
    background: #252836;
    color: #FAFAFA;
    font-size: 0.78rem;
    font-weight: 500;
    padding: 0.5rem 0.85rem;
    border-radius: 8px;
    border: 1px solid rgba(255, 107, 53, 0.3);
    white-space: nowrap;
    z-index: 100;
    pointer-events: none;
    transition: opacity 0.2s ease, visibility 0.2s ease;
    box-shadow: 0 4px 16px rgba(0,0,0,0.4);
}

.badge-pill.locked .badge-tooltip::after {
    content: '';
    position: absolute;
    top: 100%;
    left: 50%;
    transform: translateX(-50%);
    border-width: 5px;
    border-style: solid;
    border-color: #252836 transparent transparent transparent;
}

.badge-pill.locked:hover .badge-tooltip {
    visibility: visible;
    opacity: 1;
}

/* -- Custom Progress Bar ------------------------------------------------- */
.progress-container {
    background: #2A2D39;
    border-radius: 12px;
    padding: 3px;
    margin: 0.75rem 0;
}

.progress-fill {
    height: 28px;
    border-radius: 10px;
    background: linear-gradient(90deg, #FF6B35, #FFD166);
    display: flex;
    align-items: center;
    justify-content: flex-end;
    padding-right: 12px;
    font-size: 0.8rem;
    font-weight: 700;
    color: #1A1D29;
    min-width: 40px;
    transition: width 0.6s ease;
    position: relative;
    overflow: hidden;
}

.progress-fill::after {
    content: '';
    position: absolute;
    top: 0; left: -100%;
    width: 100%; height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
    animation: shimmer 2s infinite;
}

@keyframes shimmer {
    100% { left: 100%; }
}

/* -- Activity Feed Cards ------------------------------------------------- */
.activity-card {
    background: #1A1D29;
    border: 1px solid #2A2D39;
    border-radius: 12px;
    padding: 0.9rem 1.1rem;
    margin-bottom: 0.6rem;
    display: flex;
    align-items: center;
    gap: 1rem;
    transition: border-color 0.2s ease;
}

.activity-card:hover { border-color: #FF6B35; }
.activity-icon { font-size: 1.6rem; min-width: 40px; text-align: center; }
.activity-details { flex: 1; }
.activity-runner { font-weight: 700; font-size: 0.95rem; color: #FAFAFA; }
.activity-meta { font-size: 0.8rem; color: #8B8FA3; margin-top: 2px; }
.activity-distance { font-weight: 800; font-size: 1.1rem; color: #FF6B35; }

/* -- Section Headers ----------------------------------------------------- */
.section-header {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin: 1.5rem 0 1rem 0;
}

.section-header .accent-bar {
    width: 5px; height: 28px;
    border-radius: 3px;
    background: #FF6B35;
}

.section-header h3 {
    margin: 0;
    font-size: 1.25rem;
    font-weight: 700;
    color: #FAFAFA;
}

/* -- Quote Banner -------------------------------------------------------- */
.quote-banner {
    background: linear-gradient(135deg, #1A1D29 0%, #252836 100%);
    border-left: 4px solid #FF6B35;
    border-radius: 0 12px 12px 0;
    padding: 1rem 1.5rem;
    margin: 1rem 0;
    font-style: italic;
    color: #C8CADE;
    font-size: 0.95rem;
    line-height: 1.5;
}

/* -- Highlight Box ------------------------------------------------------- */
.highlight-box {
    background: rgba(6, 214, 160, 0.1);
    border: 1px solid rgba(6, 214, 160, 0.25);
    border-radius: 12px;
    padding: 1rem 1.25rem;
    margin: 0.5rem 0;
    color: #06D6A0;
    font-weight: 600;
}

.highlight-box.orange {
    background: rgba(255, 107, 53, 0.1);
    border-color: rgba(255, 107, 53, 0.25);
    color: #FF6B35;
}

/* -- DataFrames ---------------------------------------------------------- */
[data-testid="stDataFrame"] {
    border-radius: 12px;
    overflow: hidden;
}

/* -- Sidebar ------------------------------------------------------------- */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #141722 0%, #0F1117 100%);
}

/* -- Tabs ---------------------------------------------------------------- */
.stTabs [data-baseweb="tab-list"] { gap: 8px; }
.stTabs [data-baseweb="tab"] {
    border-radius: 8px 8px 0 0;
    padding: 8px 20px;
    font-weight: 600;
}

/* -- Streak Display ------------------------------------------------------ */
.streak-display {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 1.1rem;
    font-weight: 700;
    color: #FFD166;
    margin: 0.5rem 0;
}

.streak-fire {
    font-size: 1.8rem;
    animation: pulse 1.5s infinite;
}

@keyframes pulse {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.15); }
}
</style>
"""


def inject_global_css():
    """Call once at the top of every page file."""
    st.markdown(_GLOBAL_CSS, unsafe_allow_html=True)


# -- HTML Template Functions -------------------------------------------------
# IMPORTANT: All templates return compact HTML with NO blank lines.
# Streamlit's markdown parser treats blank lines as paragraph breaks,
# which terminates the HTML block and renders the rest as raw text.


def stat_card_html(icon: str, value: str, label: str, color: str = "orange") -> str:
    return (
        f'<div class="stat-card {color}">'
        f'<div class="card-icon">{icon}</div>'
        f'<div class="card-value">{value}</div>'
        f'<div class="card-label">{label}</div>'
        f'</div>'
    )


def stat_cards_row(cards: list[dict]) -> str:
    """Render a row of stat cards. Each dict needs icon, value, label, color."""
    inner = "".join(
        stat_card_html(c["icon"], c["value"], c["label"], c.get("color", "orange"))
        for c in cards
    )
    return f'<div class="stat-card-row">{inner}</div>'


def badge_pills_html(
    badges: list[str], color_cycle: list[str] | None = None
) -> str:
    """Render earned badges as colored pills."""
    if not badges:
        return '<p style="color:#8B8FA3;">No badges earned yet -- keep running!</p>'

    if color_cycle is None:
        color_cycle = ["orange", "green", "blue", "purple", "yellow", "red"]

    pills = []
    for i, badge in enumerate(badges):
        cls = color_cycle[i % len(color_cycle)]
        pills.append(f'<span class="badge-pill {cls}">{badge}</span>')

    return f'<div class="badge-container">{"".join(pills)}</div>'


def badge_pills_with_progress_html(
    all_badges: list[dict],
    color_cycle: list[str] | None = None,
) -> str:
    """
    Render all badges (earned + locked).
    Each dict: {"text": "...", "earned": True/False, "hint": "..."}
    Earned badges get color; locked badges are visible but dimmed with hover tooltip.
    """
    if color_cycle is None:
        color_cycle = ["orange", "green", "blue", "purple", "yellow", "red"]

    pills = []
    color_idx = 0
    for badge in all_badges:
        if badge["earned"]:
            cls = color_cycle[color_idx % len(color_cycle)]
            color_idx += 1
            pills.append(f'<span class="badge-pill {cls}">{badge["text"]}</span>')
        else:
            hint = badge.get("hint", "Keep going!")
            tooltip = f'<span class="badge-tooltip">🔒 {hint}</span>'
            pills.append(
                f'<span class="badge-pill locked">{badge["text"]}{tooltip}</span>'
            )

    return f'<div class="badge-container">{"".join(pills)}</div>'


def custom_progress_bar(progress: float, label: str = "") -> str:
    pct = max(0, min(100, progress * 100))
    display_label = label or f"{pct:.0f}%"
    return (
        f'<div class="progress-container">'
        f'<div class="progress-fill" style="width: {max(pct, 8)}%;">'
        f'{display_label}'
        f'</div>'
        f'</div>'
    )


def activity_card_html(
    runner: str, date: str, distance: float, run_type: str, notes: str = ""
) -> str:
    type_icons = {
        "Easy Run": "\U0001f3c3",
        "Long Run": "\U0001f3c3\u200d\u2642\ufe0f",
        "Interval": "\u26a1",
        "Race": "\U0001f3c1",
        "Recovery Run": "\U0001f9d8",
        "Other": "\U0001f45f",
    }
    icon = type_icons.get(run_type, "\U0001f45f")
    notes_html = f'<div class="activity-meta">{notes}</div>' if notes else ""
    return (
        f'<div class="activity-card">'
        f'<div class="activity-icon">{icon}</div>'
        f'<div class="activity-details">'
        f'<div class="activity-runner">{runner}</div>'
        f'<div class="activity-meta">{date} &bull; {run_type}</div>'
        f'{notes_html}'
        f'</div>'
        f'<div class="activity-distance">{distance:.1f} km</div>'
        f'</div>'
    )


def section_header(title: str) -> str:
    return (
        f'<div class="section-header">'
        f'<div class="accent-bar"></div>'
        f'<h3>{title}</h3>'
        f'</div>'
    )


def quote_banner(quote: str) -> str:
    return f'<div class="quote-banner">"{quote}"</div>'


def streak_display(weeks: int) -> str:
    if weeks <= 0:
        return '<div class="streak-display">No active streak -- get out there!</div>'
    label = "week" if weeks == 1 else "weeks"
    return (
        f'<div class="streak-display">'
        f'<span class="streak-fire">\U0001f525</span>'
        f' {weeks} {label} streak!'
        f'</div>'
    )


def highlight_box(text: str, variant: str = "green") -> str:
    cls = f"highlight-box {variant}" if variant != "green" else "highlight-box"
    return f'<div class="{cls}">{text}</div>'
