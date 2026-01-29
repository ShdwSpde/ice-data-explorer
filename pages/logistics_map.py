"""
Project Watchtower - Kinetic Logistics Map
Detention Facility Network Visualization

Visual Strategy: Pulsing nodes sized by population, colored by operator type,
connected by animated transfer route flow lines. Dark cartographic style
reveals the scale and corporate structure of the detention network.
"""

import math
import pandas as pd
import plotly.graph_objects as go
from dash import html, dcc

from database import query_data

# ---------------------------------------------------------------------------
# Color Palette
# ---------------------------------------------------------------------------
COLORS = {
    "corporate_green": "#276749",   # Private contractors (GEO/CoreCivic)
    "facade_blue": "#3d5a80",       # Government-operated facilities
    "default_gray": "#4a5568",      # Other / county-run
    "accent": "#e94560",            # Highlight / alerts
    "bg": "#0f0f23",                # Dark background
    "text": "#edf2f4",
    "text_muted": "#8d99ae",
    "grid": "#2b2d42",
    "route": "rgba(233,69,96,0.25)",  # Transfer route base color
    "route_highlight": "rgba(233,69,96,0.55)",
}

# Private contractor operators
_PRIVATE_OPERATORS = frozenset({
    "GEO Group",
    "CoreCivic",
    "LaSalle Corrections",
    "Management & Training Corp",
})

# Government operators
_GOV_OPERATORS = frozenset({
    "ICE",
})

# ---------------------------------------------------------------------------
# Transfer Routes
#
# Known high-volume inter-facility transfer corridors.  Lat/lon pairs are
# looked up from the facility data at runtime; these seed pairs define the
# network topology.  The corridors are based on publicly documented ICE
# transfer patterns (TRAC, FOIA releases).
# ---------------------------------------------------------------------------
_TRANSFER_CORRIDORS = [
    # (origin_state, dest_state, label)
    ("TX", "LA", "TX \u2192 LA corridor"),
    ("TX", "AZ", "TX \u2192 AZ transfers"),
    ("AZ", "CA", "AZ \u2192 CA transfers"),
    ("CA", "AZ", "CA \u2192 AZ returns"),
    ("GA", "FL", "GA \u2192 FL transfers"),
    ("NJ", "NY", "NJ \u2192 NY transfers"),
    ("LA", "GA", "LA \u2192 GA transfers"),
    ("TX", "GA", "TX \u2192 GA long-haul"),
    ("FL", "TX", "FL \u2192 TX transfers"),
    ("TX", "NJ", "TX \u2192 NJ long-haul"),
]


# ---------------------------------------------------------------------------
# Helper: Classify operator into color bucket
# ---------------------------------------------------------------------------

def _operator_color(operator: str) -> str:
    """Return hex color for a given facility operator."""
    if operator in _PRIVATE_OPERATORS:
        return COLORS["corporate_green"]
    if operator in _GOV_OPERATORS:
        return COLORS["facade_blue"]
    return COLORS["default_gray"]


def _operator_category(operator: str) -> str:
    """Return human-readable category label."""
    if operator in _PRIVATE_OPERATORS:
        return "Private Contractor"
    if operator in _GOV_OPERATORS:
        return "Federal Government"
    return "State / County"


# ---------------------------------------------------------------------------
# Helper: Generate curved arc points between two coordinates
# ---------------------------------------------------------------------------

def _arc_points(lat1: float, lon1: float, lat2: float, lon2: float,
                num_points: int = 30) -> tuple:
    """
    Return (lats, lons) for a smooth great-circle-style arc between two
    points, with a slight upward bow for visual clarity on the map.
    """
    lats = []
    lons = []
    for i in range(num_points + 1):
        t = i / num_points
        # Linear interpolation
        lat = lat1 + t * (lat2 - lat1)
        lon = lon1 + t * (lon2 - lon1)
        # Add parabolic vertical offset (bow) proportional to distance
        dist = math.sqrt((lat2 - lat1) ** 2 + (lon2 - lon1) ** 2)
        bow = dist * 0.15 * math.sin(math.pi * t)
        lat += bow
        lats.append(lat)
        lons.append(lon)
    return lats, lons


# ---------------------------------------------------------------------------
# Helper: Select representative facility per state for route endpoints
# ---------------------------------------------------------------------------

def _state_hub(df: pd.DataFrame, state: str) -> dict | None:
    """Return the row dict of the largest facility in *state*, or None."""
    subset = df[df["state"] == state]
    if subset.empty:
        return None
    return subset.loc[subset["current_population"].idxmax()].to_dict()


# ---------------------------------------------------------------------------
# Core: Build the logistics map figure
# ---------------------------------------------------------------------------

def _build_logistics_figure(df: pd.DataFrame) -> go.Figure:
    """Construct the Plotly figure with facility nodes and transfer routes."""
    fig = go.Figure()

    # ------------------------------------------------------------------
    # 1. Transfer route arcs (rendered first so nodes draw on top)
    # ------------------------------------------------------------------
    for origin_st, dest_st, label in _TRANSFER_CORRIDORS:
        origin = _state_hub(df, origin_st)
        dest = _state_hub(df, dest_st)
        if origin is None or dest is None:
            continue

        arc_lats, arc_lons = _arc_points(
            origin["lat"], origin["lon"],
            dest["lat"], dest["lon"],
        )

        fig.add_trace(go.Scattergeo(
            lat=arc_lats,
            lon=arc_lons,
            mode="lines",
            line=dict(width=1.5, color=COLORS["route_highlight"], dash="dot"),
            opacity=0.6,
            hoverinfo="text",
            text=label,
            showlegend=False,
        ))

        # Directional arrow-head marker at ~80% of the arc
        arrow_idx = int(len(arc_lats) * 0.8)
        fig.add_trace(go.Scattergeo(
            lat=[arc_lats[arrow_idx]],
            lon=[arc_lons[arrow_idx]],
            mode="markers",
            marker=dict(
                symbol="triangle-right",
                size=7,
                color=COLORS["accent"],
                opacity=0.7,
            ),
            hoverinfo="skip",
            showlegend=False,
        ))

    # ------------------------------------------------------------------
    # 2. Facility nodes grouped by category (for legend)
    # ------------------------------------------------------------------
    df["category"] = df["operator"].apply(_operator_category)
    df["node_color"] = df["operator"].apply(_operator_color)
    df["occupancy_pct"] = (
        df["current_population"] / df["capacity"].replace(0, 1) * 100
    ).round(1)

    # Scale marker sizes: sqrt-scale with floor and ceiling
    pop_max = df["current_population"].max() if not df.empty else 1
    df["marker_size"] = (
        df["current_population"]
        .apply(lambda p: 8 + 30 * math.sqrt(p / pop_max))
    )

    # Build hover text
    df["hover"] = df.apply(
        lambda r: (
            f"<b>{r['name']}</b><br>"
            f"{r['city']}, {r['state']}<br>"
            f"<b>Operator:</b> {r['operator']} ({r['category']})<br>"
            f"<b>Type:</b> {r['facility_type']}<br>"
            f"<br>"
            f"<b>Population:</b> {r['current_population']:,} / "
            f"{r['capacity']:,} ({r['occupancy_pct']:.0f}%)<br>"
            f"<b>Deaths:</b> {r['deaths_total']}  |  "
            f"<b>Complaints:</b> {r['complaints_total']}<br>"
            f"<b>Per Diem:</b> ${r['per_diem_rate']:,.0f}  |  "
            f"<b>Annual Contract:</b> "
            f"${r['annual_contract_value']:,.0f}<br>"
            f"<b>Inspection:</b> {r['inspection_score']}"
        ),
        axis=1,
    )

    category_order = ["Private Contractor", "Federal Government", "State / County"]
    for category in category_order:
        cat_df = df[df["category"] == category]
        if cat_df.empty:
            continue

        color = cat_df.iloc[0]["node_color"]

        # Outer glow ring (pulsing effect via larger translucent marker)
        fig.add_trace(go.Scattergeo(
            lat=cat_df["lat"],
            lon=cat_df["lon"],
            mode="markers",
            marker=dict(
                size=cat_df["marker_size"] + 8,
                color=color,
                opacity=0.15,
                line=dict(width=0),
            ),
            hoverinfo="skip",
            showlegend=False,
        ))

        # Core node
        fig.add_trace(go.Scattergeo(
            lat=cat_df["lat"],
            lon=cat_df["lon"],
            mode="markers",
            marker=dict(
                size=cat_df["marker_size"],
                color=color,
                opacity=0.85,
                line=dict(width=1, color="rgba(255,255,255,0.4)"),
                sizemode="area",
            ),
            text=cat_df["hover"],
            hoverinfo="text",
            name=category,
        ))

    # ------------------------------------------------------------------
    # 3. Layout
    # ------------------------------------------------------------------
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor=COLORS["bg"],
        plot_bgcolor=COLORS["bg"],
        font=dict(family="Source Sans Pro, sans-serif", color=COLORS["text"]),
        title=dict(
            text=(
                "<b>Detention Logistics Network</b><br>"
                "<sup>Facility nodes sized by population | "
                "Dashed lines show known transfer corridors</sup>"
            ),
            font=dict(size=20),
            x=0.5,
            xanchor="center",
        ),
        geo=dict(
            scope="usa",
            projection_type="albers usa",
            showland=True,
            landcolor="rgb(18, 18, 32)",
            showlakes=True,
            lakecolor="rgb(25, 35, 55)",
            subunitcolor="rgb(50, 50, 70)",
            countrycolor="rgb(50, 50, 70)",
            bgcolor=COLORS["bg"],
            showframe=False,
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.08,
            xanchor="center",
            x=0.5,
            font=dict(size=13),
            bgcolor="rgba(0,0,0,0)",
        ),
        margin=dict(t=90, b=80, l=10, r=10),
        height=620,
        hoverlabel=dict(
            bgcolor="rgba(15,15,35,0.92)",
            bordercolor=COLORS["accent"],
            font_size=13,
            font_family="Source Sans Pro, sans-serif",
        ),
    )

    return fig


# ---------------------------------------------------------------------------
# Helper: Summary stat cards
# ---------------------------------------------------------------------------

def _build_stat_cards(df: pd.DataFrame) -> html.Div:
    """Return a row of summary statistic cards derived from the dataframe."""
    total_pop = int(df["current_population"].sum())
    total_cap = int(df["capacity"].sum())
    overall_occ = round(total_pop / total_cap * 100, 1) if total_cap else 0
    total_deaths = int(df["deaths_total"].sum())
    total_complaints = int(df["complaints_total"].sum())
    total_contract = df["annual_contract_value"].sum()
    num_facilities = len(df)

    private_pop = int(
        df.loc[df["operator"].isin(_PRIVATE_OPERATORS), "current_population"].sum()
    )
    private_pct = round(private_pop / total_pop * 100, 1) if total_pop else 0

    cards = [
        ("Active Facilities", f"{num_facilities}", None),
        ("Total Population", f"{total_pop:,}", f"of {total_cap:,} capacity"),
        ("Occupancy", f"{overall_occ}%", None),
        ("Deaths Recorded", f"{total_deaths}", None),
        ("Complaints Filed", f"{total_complaints:,}", None),
        (
            "Annual Contract Value",
            f"${total_contract / 1e9:.2f}B",
            None,
        ),
        (
            "Private Contractor Share",
            f"{private_pct}%",
            f"{private_pop:,} detainees",
        ),
    ]

    card_elements = []
    for title, value, subtitle in cards:
        children = [
            html.Div(title, style={
                "fontSize": "0.75rem",
                "textTransform": "uppercase",
                "letterSpacing": "0.08em",
                "color": COLORS["text_muted"],
                "marginBottom": "4px",
            }),
            html.Div(value, style={
                "fontSize": "1.6rem",
                "fontWeight": "700",
                "color": COLORS["text"],
                "lineHeight": "1.2",
            }),
        ]
        if subtitle:
            children.append(html.Div(subtitle, style={
                "fontSize": "0.75rem",
                "color": COLORS["text_muted"],
                "marginTop": "2px",
            }))
        card_elements.append(
            html.Div(children, style={
                "backgroundColor": "rgba(30,30,55,0.7)",
                "border": f"1px solid {COLORS['grid']}",
                "borderRadius": "8px",
                "padding": "16px 20px",
                "minWidth": "140px",
                "flex": "1 1 140px",
            })
        )

    return html.Div(
        card_elements,
        style={
            "display": "flex",
            "flexWrap": "wrap",
            "gap": "12px",
            "marginBottom": "24px",
        },
    )


# ---------------------------------------------------------------------------
# Helper: Legend strip
# ---------------------------------------------------------------------------

def _build_legend_strip() -> html.Div:
    """Inline color legend matching facility node categories."""
    items = [
        (COLORS["corporate_green"], "Private Contractor (GEO / CoreCivic / LaSalle / MTC)"),
        (COLORS["facade_blue"], "Federal Government (ICE-operated)"),
        (COLORS["default_gray"], "State / County"),
        (COLORS["accent"], "Transfer Corridor"),
    ]

    legend_children = []
    for color, label in items:
        legend_children.append(
            html.Div([
                html.Span(style={
                    "display": "inline-block",
                    "width": "12px",
                    "height": "12px",
                    "borderRadius": "50%",
                    "backgroundColor": color,
                    "marginRight": "6px",
                    "verticalAlign": "middle",
                }),
                html.Span(label, style={
                    "fontSize": "0.82rem",
                    "color": COLORS["text_muted"],
                }),
            ], style={
                "display": "inline-flex",
                "alignItems": "center",
                "marginRight": "24px",
            })
        )

    return html.Div(
        legend_children,
        style={
            "display": "flex",
            "flexWrap": "wrap",
            "gap": "8px",
            "marginTop": "12px",
            "marginBottom": "8px",
        },
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_logistics_map_content() -> html.Div:
    """
    Build and return the full logistics map page content.

    Returns a Dash ``html.Div`` containing:
    * Summary statistic cards
    * Interactive Scattergeo map with pulsing facility nodes and transfer arcs
    * Color legend strip
    * Methodology footnote
    """
    # ------------------------------------------------------------------
    # Data fetch
    # ------------------------------------------------------------------
    rows = query_data(
        "SELECT * FROM detention_facilities "
        "WHERE current_population > 0 "
        "ORDER BY current_population DESC"
    )
    df = pd.DataFrame(rows)

    # ------------------------------------------------------------------
    # Empty-state guard
    # ------------------------------------------------------------------
    if df.empty:
        return html.Div(
            html.P(
                "No facility data available. Please verify the database has been seeded.",
                style={"color": COLORS["text_muted"], "padding": "40px"},
            )
        )

    # ------------------------------------------------------------------
    # Assemble figure
    # ------------------------------------------------------------------
    fig = _build_logistics_figure(df)

    # ------------------------------------------------------------------
    # Page layout
    # ------------------------------------------------------------------
    return html.Div([
        # Header
        html.Div([
            html.H2(
                "Detention Logistics Network",
                className="section-title",
            ),
            html.P([
                "A kinetic view of the ICE detention network. ",
                "Nodes represent active facilities sized by current population "
                "and colored by operator type. ",
                "Dashed arcs trace documented inter-facility transfer corridors."
            ], className="section-intro"),
        ], className="container"),

        # Stats row
        html.Div(
            _build_stat_cards(df),
            className="container",
        ),

        # Map
        html.Div(
            dcc.Graph(
                id="logistics-map-graph",
                figure=fig,
                config={
                    "displayModeBar": True,
                    "modeBarButtonsToRemove": [
                        "select2d", "lasso2d", "autoScale2d",
                        "hoverClosestGeo",
                    ],
                    "scrollZoom": False,
                    "displaylogo": False,
                },
                style={"width": "100%"},
            ),
            className="map-container",
        ),

        # Legend
        html.Div(
            _build_legend_strip(),
            className="container",
        ),

        # Methodology note
        html.Div([
            html.P([
                html.Strong("Methodology: "),
                "Facility locations, populations, and contract data sourced from "
                "ICE Enforcement and Removal Operations reports, DHS OIG inspection "
                "records, and FOIA releases. Transfer corridors reflect documented "
                "inter-facility movement patterns reported by TRAC Immigration and "
                "investigative journalism. Node sizes use square-root scaling to "
                "preserve visual proportionality across the wide population range."
            ], style={
                "fontSize": "0.8rem",
                "color": COLORS["text_muted"],
                "lineHeight": "1.6",
                "maxWidth": "860px",
            }),
        ], className="container", style={"marginTop": "18px", "marginBottom": "40px"}),
    ])
