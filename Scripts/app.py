from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from streamlit_main import generate_pitcher_report
from milb_directory import MILB_AFFILIATE_ORG

SCRIPT_DIR = Path(__file__).resolve().parent
LOGO_DIR = SCRIPT_DIR / "logos"


st.set_page_config(
    page_title="Pitcher Scouting Report",
    page_icon="⚾",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
        header[data-testid="stHeader"] {display: none;}
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}

        .block-container {
            max-width: 1750px;
            padding-top: 0.8rem;
            padding-bottom: 0.8rem;
        }

        h1, h2, h3 {margin-top: 0;}

        .app-title {
            color: #1f2937;
            font-size: 2.25rem;
            font-weight: 800;
            line-height: 1.15;
            margin: 0 0 0.2rem 0;
            position: relative;
            z-index: 10;
        }

        .app-subtitle {
            color: #5f6368;
            margin-bottom: 1rem;
        }

        .section-label {
            border-bottom: 2px solid #111;
            font-size: 1rem;
            font-weight: 800;
            letter-spacing: 0.02em;
            margin-bottom: 0.45rem;
            padding-bottom: 0.2rem;
            text-align: center;
            text-transform: uppercase;
        }

        .player-name {
            font-size: 1.95rem;
            font-weight: 800;
            line-height: 1.1;
            margin-bottom: 0.35rem;
        }

        .team-name {
            font-size: 1.25rem;
            font-weight: 800;
            margin-bottom: 0.15rem;
        }

        .player-detail {
            font-size: 1.05rem;
            line-height: 1.45;
        }

        .split-banner {
            border: 2px solid #111;
            font-size: 1.15rem;
            font-weight: 800;
            margin-top: 0.5rem;
            padding: 0.35rem;
            text-align: center;
        }

        .season-stats-panel {
            position: relative;
            top: -1.15rem;
            width: 100%;
        }

        .season-stats-title {
            border-bottom: 2px solid #111;
            font-size: 1.05rem;
            font-weight: 800;
            letter-spacing: 0.02em;
            margin: 0 0 0.65rem 0;
            padding-bottom: 0.28rem;
            text-align: center;
            text-transform: uppercase;
        }

        .season-grid {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            column-gap: 1.6rem;
            row-gap: 1rem;
            padding: 0;
        }

        .season-stat {
            text-align: center;
        }

        .season-stat-label {
            font-size: 1rem;
            font-weight: 800;
            line-height: 1.1;
            margin-bottom: 0.28rem;
        }

        .season-stat-value {
            font-size: 1.55rem;
            font-weight: 400;
            line-height: 1.1;
        }

        div[data-testid="stDataFrame"] {border: 1px solid #111;}

        [data-testid="stImage"] img {object-fit: contain;}

        .small-note {
            color: #666;
            font-size: 0.78rem;
            text-align: center;
        }

        @media (max-width: 900px) {
            .block-container {
                padding-left: 0.6rem;
                padding-right: 0.6rem;
            }
            .season-grid {grid-template-columns: repeat(2, minmax(0, 1fr));}
        }
    </style>
    """,
    unsafe_allow_html=True,
)


def display_value(value: Any, suffix: str = "", label: str = "",) -> str:
    if value is None or value == "":
        return "—"

    if isinstance(value, (int, float)):
        if pd.isna(value):
            return "—"

        # Percentages always show one decimal place
        if suffix == "%":
            value = f"{value:.1f}"

        # ERA, WHIP, and FIP always show two decimal places
        elif label in {"ERA", "WHIP", "FIP"}:
            value = f"{value:.2f}"

        # Everything else displays naturally
        else:
            value = f"{value:g}"

    return f"{value}{suffix}"


def show_figure(
    figure: Any,
    *,
    width: float | None = None,
    height: float | None = None,
    stretch: bool = True,
) -> None:
    if figure is None:
        st.info("No chart available.")
        return

    if (
        width is not None
        and height is not None
        and hasattr(figure, "set_size_inches")
    ):
        figure.set_size_inches(
            width,
            height,
            forward=True,
        )

        try:
            figure.tight_layout(pad=0.8)
        except Exception:
            pass

    st.pyplot(
        figure,
        width="stretch" if stretch else "content",
        clear_figure=False,
    )



def format_percentage_columns(table: pd.DataFrame) -> pd.DataFrame:
    """Add percent signs to all percentage-based table columns."""
    display = table.copy()

    explicit_percent_columns = {
        "0-0",
        "0-1",
        "0-2",
        "1-0",
        "1-1",
        "1-2",
        "2-0",
        "2-1",
        "2-2",
        "3-0",
        "3-1",
        "3-2",
        "w/ 2 Strikes",
        "W/ 2 Strikes",
        "w/2 Strikes",
        "W/2 Strikes",
        }

    def format_percent(value):
        if value is None:
            return ""

        try:
            if pd.isna(value):
                return ""
        except TypeError:
            pass

        text = str(value).strip()

        if not text or text.lower() in {"nan", "none"}:
            return ""

        if text.endswith("%"):
            return text

        try:
            number = float(value)
            return f"{number:.1f}%"
        except (TypeError, ValueError):
            return f"{text}%"

    for column in display.columns:
        column_name = str(column).strip()

        if (
            "%" in column_name
            or column_name in explicit_percent_columns
        ):
            display[column] = display[column].map(
                format_percent
            )

    return display

def resolve_logo_path(info: dict) -> Path | None:
    """
    Resolve the team's logo using the MLB abbreviation returned
    by player_info.py.
    """

    team_abbr = str(info.get("team_abbr", "")).strip().upper()
    # Convert MiLB affiliate to MLB organization if applicable
    team_abbr = MILB_AFFILIATE_ORG.get(team_abbr, team_abbr)

    if not team_abbr:
        return None

    logo_path = LOGO_DIR / f"{team_abbr}.png"

    if logo_path.exists():
        return logo_path

    return None


def season_stats_html(header: dict, role: str) -> str:
    games = display_value(header.get("G"))
    starts = display_value(header.get("GS"))

    # Match the starter/reliever designation already calculated in player_info.py.
    # Starting pitchers show per-start values; relievers show per-game values.
    if str(role).upper() == "SP":
        workload_stats = [
            ("IP/GS", header.get("IP/GS"), ""),
            ("Pitches/GS", header.get("Pitches/GS"), ""),
        ]
    else:
        workload_stats = [
            ("IP/G", header.get("IP/G"), ""),
            ("Pitches/G", header.get("Pitches/G"), ""),
        ]

    stats = [
        ("IP", header.get("IP"), ""),
        ("ERA", header.get("ERA"), ""),
        ("FIP", header.get("FIP"), ""),
        ("WHIP", header.get("WHIP"), ""),
        ("K%", header.get("K%"), "%"),
        ("BB%", header.get("BB%"), "%"),
        ("G/GS", f"{games}/{starts}", ""),
        *workload_stats,
    ]

    cells = "".join(
        f'<div class="season-stat">'
        f'<div class="season-stat-label">{label}</div>'
        f'<div class="season-stat-value">'
        f'{display_value(value, suffix=suffix, label=label,)}'
        f'</div>'
        f'</div>'
        for label, value, suffix in stats
    )

    return f"""
    <div class="season-stats-panel">
        <div class="season-stats-title">Season Stats</div>
        <div class="season-grid">
            {cells}
        </div>
    </div>
    """


def show_player_header(shared: dict, split_label: str) -> None:
    info = shared.get("player_info") or {}
    header = shared.get("header") or {}

    with st.container(border=True):
        headshot_col, player_col, logo_col, stats_col = st.columns(
            [1.0, 1.45, 1.3, 3.75], gap="medium", vertical_alignment="center"
        )

        with headshot_col:
            headshot = shared.get("headshot_file")
            if headshot and Path(headshot).exists():
                st.image(headshot, width='stretch')
            else:
                st.caption("Headshot unavailable")

        with player_col:
            st.markdown(
                f'<div class="player-name">{shared.get("official_name", "")}</div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                f"""
                <div class="team-name">
                    {display_value(info.get('team'))}
                </div>

                <div class="player-detail">
                    Pos: {display_value(info.get('role'))}<br>
                    Throws: {display_value(info.get('throws'))}<br>
                    Age: {display_value(info.get('age'))}<br>
                    Height: {display_value(info.get('height'))}
                </div>
                """,
                unsafe_allow_html=True,
            )

        with logo_col:
            logo_path = resolve_logo_path(info)
            if logo_path:
                st.image(str(logo_path), width='stretch')
            else:
                st.markdown('<div class="small-note">Team logo unavailable</div>', unsafe_allow_html=True)

            st.markdown(f'<div class="split-banner">{split_label}</div>', unsafe_allow_html=True)

        with stats_col:
            st.markdown(
                season_stats_html(
                    header,
                    info.get("role", ""),
                ),
                unsafe_allow_html=True,
            )


def clean_table(table: pd.DataFrame) -> pd.DataFrame:
    display = table.copy().reset_index()
    display = display.dropna(axis=0, how="all")
    display = display.loc[~display.apply(lambda row: row.astype(str).str.strip().isin(["", "nan", "None"]).all(), axis=1)]
    return display.reset_index(drop=True)


def prepare_table_one(table: pd.DataFrame) -> pd.DataFrame:
    display = clean_table(table)
    first_column = display.columns[0]
    display = display.rename(columns={
        first_column: "Pitch Type", "Pitch_Count": "#", "Usage": "Usage%",
        "Usage_Last30": "Last 30 Days Usage%", "Max_Velo": "Max", "Avg_IVB": "IVB (in)", "Avg_HB": "HB (in)", "Avg_Release_Height": "Release Hgt (ft)",
    })
    return format_percentage_columns(display)


def prepare_table_two(table: pd.DataFrame) -> pd.DataFrame:
    display = clean_table(table)
    first_column = display.columns[0]
    display = display.rename(columns={
        first_column: "Pitch Type", "Usage": "Usage%",
    })
    return format_percentage_columns(display)


def dynamic_table_height(table: pd.DataFrame) -> int:
    rows = max(len(table), 1)
    return min(44 + rows * 35, 520)


def show_table_one(table: pd.DataFrame) -> None:
    st.dataframe(
        table,
        width='stretch',
        hide_index=True,
        height=dynamic_table_height(table),
        row_height=34,
    )


def show_count_table(table: pd.DataFrame) -> None:
    """
    Render the Pitch Results and Count Usage table responsively.

    On desktop:
        The table stretches across the report width.

    On smaller screens:
        Columns remain readable and can be scrolled horizontally.
    """
    if table is None or table.empty:
        st.info(
            "No pitch results or count usage data available for this split."
        )
        return

    st.dataframe(
        table,
        width="stretch",
        hide_index=True,
        height=dynamic_table_height(table),
        row_height=38,
    )

def heatmap_columns(count: int) -> int:
    if count <= 1:
        return 1
    if count <= 4:
        return count
    if count <= 8:
        return 4
    return 5


def show_heatmaps(heatmaps: dict) -> None:
    with st.container(border=True):
        st.markdown(
            '<div class="section-label">Pitch Location Heatmaps</div>',
            unsafe_allow_html=True,
        )

        if not heatmaps:
            st.info("No heatmaps were generated for this split.")
            return

        items = list(heatmaps.items())
        columns_per_row = heatmap_columns(len(items))

        for start_index in range(0, len(items), columns_per_row):
            row_items = items[
                start_index:start_index + columns_per_row
            ]

            items_in_row = len(row_items)

            # Full row: use the normal layout.
            if items_in_row == columns_per_row:
                columns = st.columns(
                    columns_per_row,
                    gap="small",
                )

                for column, (_, figure) in zip(
                    columns,
                    row_items,
                ):
                    with column:
                        show_figure(figure, width=1.5, height=2.05)

            # Partial row: add equal spacer columns
            # on the left and right to center it.
            else:
                empty_slots = columns_per_row - items_in_row

                left_weight = empty_slots / 2
                right_weight = empty_slots / 2

                column_weights = (
                    [left_weight]
                    + [1] * items_in_row
                    + [right_weight]
                )

                columns = st.columns(
                    column_weights,
                    gap="small",
                )

                heatmap_columns_only = columns[
                    1:1 + items_in_row
                ]

                for column, (_, figure) in zip(
                    heatmap_columns_only,
                    row_items,
                ):
                    with column:
                        show_figure(figure, width=1.5, height=2.05)


def show_report_page(shared: dict, page: dict) -> None:
    show_player_header(shared, page["split_label"])
    st.write("")

   # Supporting graphics on the left, pitch movement on the right.
    support_col, movement_col = st.columns(
        [1.45, 2.55],
        gap="medium",
        vertical_alignment="top",
    )

    with support_col:
        with st.container(border=True):
            st.markdown(
                '<div class="section-label">Arm Angle</div>',
                unsafe_allow_html=True,
            )

            _, arm_image_col, _ = st.columns([0.25, 0.50, 0.25], gap=None,)

            with arm_image_col:
                show_figure(shared.get("arm_angle"), stretch=False,)

        st.markdown(
            "<div style='height:4px;'></div>",
            unsafe_allow_html=True,
        )

        with st.container(border=True):
            st.markdown(
                '<div class="section-label">Extension</div>',
                unsafe_allow_html=True,
            )

            _, extension_image_col, _ = st.columns([0.25, 0.50, 0.25], gap=None,)

            with extension_image_col:
                show_figure(shared.get("extension"), stretch=False,)

    with movement_col:
        with st.container(border=True):
            st.markdown(
                '<div class="section-label">Pitch Movement</div>',
                unsafe_allow_html=True,
            )
            show_figure(
                page.get("movement_plot"),
                width=7.6,
                height=4.5,
            )

    st.write("")

    # Pitch arsenal now spans the full report width directly beneath the graphics.
    with st.container(border=True):
        st.markdown('<div class="section-label">Pitch Characteristics</div>', unsafe_allow_html=True)
        show_table_one(prepare_table_one(page["display_table_one"]))

    st.write("")
    show_heatmaps(page.get("heatmaps") or {})
    st.write("")

    with st.container(border=True):
        st.markdown('<div class="section-label">Pitch Results and Count Usage</div>', unsafe_allow_html=True)
        show_count_table(prepare_table_two(page["display_table_two"]))


st.markdown('<div class="app-title">Advance Scouting Report</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="app-subtitle">Enter a full pitcher name to generate the scouting dashboard.</div>',
    unsafe_allow_html=True,
)

with st.form("pitcher_search", clear_on_submit=False):
    search_col, button_col = st.columns([5, 1], vertical_alignment="bottom")
    with search_col:
        pitcher_name = st.text_input(
            "Pitcher name", placeholder="Example: Sean Burke", label_visibility="collapsed"
        )
    with button_col:
        submitted = st.form_submit_button("Generate Report", type="primary", width='stretch')

if submitted:
    pitcher_name = pitcher_name.strip()
    if not pitcher_name:
        st.warning("Enter the pitcher's first and last name.")
        st.stop()

    try:
        with st.spinner(f"Generating report for {pitcher_name}..."):
            report = generate_pitcher_report(pitcher_name)

        st.success(f'Report generated for {report["shared"]["official_name"]}.')
        split_names = ["Overall", "vs RHH", "vs LHH"]
        tabs = st.tabs(split_names)
        for tab, split_name in zip(tabs, split_names):
            with tab:
                show_report_page(report["shared"], report["pages"][split_name])

    except Exception as error:
        st.error(f"Unable to generate report: {error}")
        with st.expander("Technical details"):
            st.exception(error)
