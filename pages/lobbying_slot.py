"""
Project Watchtower - Lobbying ROI Slot Machine
FR 3.5: Visualize return on lobbying investment

Visual Strategy: Interactive "slot machine" showing how lobbying dollars
translate into contract awards. Pull the lever to see the ROI spin up.
Gamifies the corrupt relationship between lobbying and contracts.
"""

import plotly.graph_objects as go
from dash import html, dcc, callback, Input, Output, State, clientside_callback
import random

# Import data
try:
    from data.lobbying_data import get_lobbying_client, get_lobbying_summary
except ImportError:
    from data.lobbying_data import get_lobbying_client, get_lobbying_summary


# Color palette
COLORS = {
    'bg': '#0f0f23',
    'slot_bg': '#1a1a2e',
    'gold': '#d69e2e',
    'green': '#276749',
    'red': '#e53e3e',
    'text': '#e2e8f0',
    'text_muted': '#8d99ae',
    'jackpot': '#ffd700',
}

# Company data for slot machine
SLOT_DATA = [
    {
        'name': 'GEO Group',
        'lobbying': 12500000,
        'contracts': 892000000,
        'roi': 71,
        'symbol': '🏢',
        'jackpot_text': '$71 back for every $1 lobbied!',
    },
    {
        'name': 'CoreCivic',
        'lobbying': 8200000,
        'contracts': 756000000,
        'roi': 92,
        'symbol': '🔒',
        'jackpot_text': '$92 back for every $1 lobbied!',
    },
    {
        'name': 'Palantir',
        'lobbying': 4800000,
        'contracts': 340000000,
        'roi': 71,
        'symbol': '👁️',
        'jackpot_text': '$71 back for every $1 lobbied!',
    },
    {
        'name': 'Northrop Grumman',
        'lobbying': 7120000,  # Immigration-related portion
        'contracts': 890000000,
        'roi': 125,
        'symbol': '🛡️',
        'jackpot_text': '$125 back for every $1 lobbied!',
    },
    {
        'name': 'LexisNexis',
        'lobbying': 3200000,
        'contracts': 156000000,
        'roi': 49,
        'symbol': '🔍',
        'jackpot_text': '$49 back for every $1 lobbied!',
    },
]


def create_roi_bar_chart():
    """Create a bar chart showing ROI by company."""
    companies = [d['name'] for d in SLOT_DATA]
    rois = [d['roi'] for d in SLOT_DATA]
    colors = [COLORS['gold'] if r >= 70 else COLORS['green'] for r in rois]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=companies,
        y=rois,
        marker_color=colors,
        text=[f'${r}' for r in rois],
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>ROI: $%{y} per $1 lobbied<extra></extra>',
    ))

    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor=COLORS['bg'],
        plot_bgcolor=COLORS['bg'],
        font=dict(family='IBM Plex Sans, sans-serif', color=COLORS['text']),
        title=dict(
            text='<b>Return on Lobbying Investment</b><br>'
                 '<sup>Contract dollars received per lobbying dollar spent</sup>',
            font=dict(size=16),
            x=0.5,
        ),
        xaxis=dict(showgrid=False),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(255,255,255,0.05)',
            title='$ Return per $1 Lobbied',
        ),
        margin=dict(t=80, b=40, l=60, r=30),
        height=350,
        showlegend=False,
    )

    return fig


def create_slot_reel(company_data):
    """Create a slot machine reel display for a company."""
    return html.Div([
        html.Div([
            html.Div(company_data['symbol'], className='slot-symbol'),
            html.Div(company_data['name'], className='slot-name'),
        ], className='slot-reel-display'),
        html.Div([
            html.Div([
                html.Span("Lobbying:", className='slot-label'),
                html.Span(f"${company_data['lobbying']/1000000:.1f}M", className='slot-value lobbying'),
            ], className='slot-stat'),
            html.Div([
                html.Span("Contracts:", className='slot-label'),
                html.Span(f"${company_data['contracts']/1000000:.0f}M", className='slot-value contracts'),
            ], className='slot-stat'),
            html.Div([
                html.Span("ROI:", className='slot-label'),
                html.Span(f"${company_data['roi']}:$1", className='slot-value roi'),
            ], className='slot-stat roi-stat'),
        ], className='slot-stats'),
        html.Div(company_data['jackpot_text'], className='jackpot-text'),
    ], className='slot-reel')


def create_slot_machine():
    """Create the interactive slot machine display."""
    return html.Div([
        html.Div([
            html.Div("🎰", className='slot-header-icon'),
            html.H3("LOBBYING JACKPOT", className='slot-header-title'),
            html.Div("Pull to see what lobbying buys!", className='slot-header-subtitle'),
        ], className='slot-header'),

        html.Div([
            html.Div(
                [create_slot_reel(d) for d in SLOT_DATA[:3]],
                className='slot-reels',
                id='slot-reels'
            ),
        ], className='slot-window'),

        html.Button([
            html.Span("🎰", className='lever-icon'),
            html.Span("PULL LEVER", className='lever-text'),
        ], id='pull-lever-btn', className='lever-button'),

        html.Div([
            html.Div("Average ROI across tracked companies:", className='average-label'),
            html.Div("$82 in contracts per $1 lobbied", className='average-value'),
        ], className='average-display'),

    ], className='slot-machine')


def get_lobbying_slot_content():
    """
    Build and return the Lobbying ROI Slot Machine page.

    Returns:
        Dash html.Div with the slot machine visualization
    """
    summary = get_lobbying_summary()
    roi_chart = create_roi_bar_chart()

    # Calculate totals
    total_lobbying = sum(d['lobbying'] for d in SLOT_DATA)
    total_contracts = sum(d['contracts'] for d in SLOT_DATA)
    avg_roi = total_contracts / total_lobbying

    return html.Div([
        # Header
        html.Div([
            html.Div([
                html.H2("The Lobbying Jackpot", className='section-title'),
                html.P([
                    "What's the return on investment for lobbying Congress? For private prison ",
                    "companies and surveillance tech vendors, the answer is staggering. Every dollar ",
                    "spent on lobbying returns tens of dollars in government contracts."
                ], className='section-intro'),
            ], className='container'),
        ], className='slot-page-header'),

        # Key statistics
        html.Div([
            html.Div([
                html.Div([
                    html.Div([
                        html.Span("Total Lobbying", className='stat-label'),
                        html.Span(f"${total_lobbying/1000000:.0f}M", className='stat-value'),
                    ], className='slot-stat'),
                    html.Div([
                        html.Span("Total Contracts", className='stat-label'),
                        html.Span(f"${total_contracts/1000000000:.1f}B", className='stat-value'),
                    ], className='slot-stat'),
                    html.Div([
                        html.Span("Average ROI", className='stat-label'),
                        html.Span(f"${avg_roi:.0f}:$1", className='stat-value stat-gold'),
                    ], className='slot-stat'),
                    html.Div([
                        html.Span("Best Performer", className='stat-label'),
                        html.Span("Northrop Grumman", className='stat-value'),
                        html.Span("($125:$1)", className='stat-note'),
                    ], className='slot-stat'),
                ], className='slot-stats-row'),
            ], className='container'),
        ], className='slot-stats-bar'),

        # Slot machine
        html.Div([
            html.Div([
                create_slot_machine(),
            ], className='container'),
        ], className='slot-machine-section'),

        # ROI chart
        html.Div([
            html.Div([
                dcc.Graph(
                    id='roi-chart',
                    figure=roi_chart,
                    config={'displayModeBar': False},
                ),
            ], className='container'),
        ], className='chart-section'),

        # How it works
        html.Div([
            html.Div([
                html.H3("How the Game is Played", className='subsection-title'),
                html.Div([
                    html.Div([
                        html.Div("1", className='step-number'),
                        html.H4("Hire Lobbyists", className='step-title'),
                        html.P("Companies spend millions on former officials and connected firms.",
                              className='step-text'),
                    ], className='game-step'),
                    html.Div([
                        html.Div("2", className='step-number'),
                        html.H4("Target Committees", className='step-title'),
                        html.P("Lobbying focuses on Appropriations and Homeland Security.",
                              className='step-text'),
                    ], className='game-step'),
                    html.Div([
                        html.Div("3", className='step-number'),
                        html.H4("Push Policy", className='step-title'),
                        html.P("Advocate for mandatory detention, bed quotas, tech mandates.",
                              className='step-text'),
                    ], className='game-step'),
                    html.Div([
                        html.Div("4", className='step-number'),
                        html.H4("Win Contracts", className='step-title'),
                        html.P("When policy changes, be first in line for implementation contracts.",
                              className='step-text'),
                    ], className='game-step'),
                ], className='game-steps'),
            ], className='container'),
        ], className='how-it-works-section'),

        # The house always wins callout
        html.Div([
            html.Div([
                html.Div([
                    html.H3("The House Always Wins", className='pattern-title'),
                    html.P([
                        "In this casino, the odds are rigged. Companies that lobby for harsher ",
                        "immigration enforcement consistently win contracts to implement that enforcement. ",
                        "It's not gambling when you help write the rules."
                    ], className='pattern-text'),
                    html.P([
                        "For every $1 these companies spend influencing policy, they receive ",
                        html.Strong(f"${avg_roi:.0f} in taxpayer-funded contracts. "),
                        "That's not a market—it's a money machine."
                    ], className='pattern-text'),
                ], className='pattern-box'),
            ], className='container'),
        ], className='pattern-section'),

        # Methodology
        html.Div([
            html.Div([
                html.H4("Data Sources", className='methodology-title'),
                html.P([
                    "Lobbying expenditures from OpenSecrets.org (LDA filings). ",
                    "Contract values from USASpending.gov. ",
                    "ROI calculated as (total DHS/ICE contracts) / (total lobbying spend) for each company. ",
                    "For defense contractors, only immigration-related contract portions are included."
                ], className='methodology-text'),
            ], className='container'),
        ], className='slot-methodology'),

    ], className='lobbying-slot-page')


# Clientside callback for slot machine animation
SLOT_ANIMATION_JS = """
function(n_clicks) {
    if (n_clicks) {
        const reels = document.getElementById('slot-reels');
        if (reels) {
            reels.classList.add('spinning');
            setTimeout(() => {
                reels.classList.remove('spinning');
                reels.classList.add('winner');
            }, 2000);
            setTimeout(() => {
                reels.classList.remove('winner');
            }, 4000);
        }
    }
    return window.dash_clientside.no_update;
}
"""
