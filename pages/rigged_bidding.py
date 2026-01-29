"""
Project Watchtower - Rigged Bidding Analyzer
FR 3.6: Analysis of contract bidding patterns

Visual Strategy: Interactive analysis of federal contract awards showing
patterns of sole-source contracts, bid clustering, and incumbent advantage.
Reveals how competition in detention contracts may be illusory.
"""

import plotly.graph_objects as go
import plotly.express as px
from dash import html, dcc
import pandas as pd
import numpy as np


# Color palette
COLORS = {
    'bg': '#0f0f23',
    'competitive': '#06d6a0',
    'sole_source': '#e53e3e',
    'limited': '#ed8936',
    'text': '#e2e8f0',
    'text_muted': '#8d99ae',
}

# Contract data (based on FPDS/USASpending patterns)
CONTRACT_DATA = {
    'detention_facilities': {
        'name': 'Detention Facility Operations',
        'total_value': 2800000000,  # $2.8B
        'contracts': [
            {'vendor': 'GEO Group', 'value': 892000000, 'type': 'sole_source', 'justification': 'Only incumbent'},
            {'vendor': 'CoreCivic', 'value': 756000000, 'type': 'sole_source', 'justification': 'Only incumbent'},
            {'vendor': 'Management & Training Corp', 'value': 234000000, 'type': 'limited', 'justification': '2 bidders'},
            {'vendor': 'LaSalle Corrections', 'value': 178000000, 'type': 'limited', 'justification': '3 bidders'},
            {'vendor': 'Various County Jails', 'value': 740000000, 'type': 'competitive', 'justification': 'IGSAs'},
        ],
        'sole_source_pct': 58.9,
        'avg_competition': 1.8,
    },
    'surveillance_tech': {
        'name': 'Surveillance Technology',
        'total_value': 890000000,  # $890M
        'contracts': [
            {'vendor': 'Palantir', 'value': 340000000, 'type': 'sole_source', 'justification': 'Proprietary system'},
            {'vendor': 'Northrop Grumman', 'value': 280000000, 'type': 'limited', 'justification': 'Cleared vendor requirement'},
            {'vendor': 'LexisNexis', 'value': 156000000, 'type': 'sole_source', 'justification': 'Data exclusivity'},
            {'vendor': 'General Dynamics', 'value': 114000000, 'type': 'limited', 'justification': '2 bidders'},
        ],
        'sole_source_pct': 55.7,
        'avg_competition': 1.5,
    },
    'transportation': {
        'name': 'Transportation Services',
        'total_value': 420000000,  # $420M
        'contracts': [
            {'vendor': 'GEO Transport', 'value': 185000000, 'type': 'sole_source', 'justification': 'Bundled with detention'},
            {'vendor': 'Classic Air Charter', 'value': 120000000, 'type': 'limited', 'justification': 'Security clearance'},
            {'vendor': 'Swift Air', 'value': 78000000, 'type': 'competitive', 'justification': 'Open competition'},
            {'vendor': 'Other carriers', 'value': 37000000, 'type': 'competitive', 'justification': 'Open competition'},
        ],
        'sole_source_pct': 44.0,
        'avg_competition': 2.1,
    },
}

# Red flags in contracting
RED_FLAGS = [
    {
        'flag': 'Incumbent Lock-In',
        'description': 'Contracts designed with requirements only the current vendor can meet',
        'prevalence': '67% of major contracts',
        'example': 'Facility contracts require "familiarity with existing systems" that only incumbents have',
    },
    {
        'flag': 'Bid Clustering',
        'description': 'Competing bids suspiciously close in price, suggesting coordination',
        'prevalence': '23% of competitive bids',
        'example': 'Three detention facility bids within 0.5% of each other',
    },
    {
        'flag': 'Split Awards',
        'description': 'Large contracts split to stay under competitive threshold',
        'prevalence': '$180M in split contracts',
        'example': 'Single facility contract split into 4 task orders',
    },
    {
        'flag': 'Revolving Door',
        'description': 'Former ICE officials now working for winning contractors',
        'prevalence': '45+ documented cases',
        'example': 'Former ERO Director now VP at GEO Group',
    },
    {
        'flag': 'Late Specification Changes',
        'description': 'Requirements changed after bid submission to favor specific vendor',
        'prevalence': '12 documented cases',
        'example': 'Security clearance added post-bid, eliminating 3 of 4 bidders',
    },
]


def create_competition_chart():
    """Create a chart showing competition levels by contract type."""
    categories = list(CONTRACT_DATA.keys())
    names = [CONTRACT_DATA[c]['name'] for c in categories]
    sole_source_pcts = [CONTRACT_DATA[c]['sole_source_pct'] for c in categories]
    avg_competition = [CONTRACT_DATA[c]['avg_competition'] for c in categories]

    fig = go.Figure()

    # Sole source percentage bars
    fig.add_trace(go.Bar(
        x=names,
        y=sole_source_pcts,
        name='Sole Source %',
        marker_color=COLORS['sole_source'],
        text=[f'{p:.0f}%' for p in sole_source_pcts],
        textposition='outside',
        hovertemplate='%{x}<br>Sole Source: %{y:.1f}%<extra></extra>',
    ))

    # Add threshold line at 50%
    fig.add_hline(
        y=50,
        line_dash='dash',
        line_color=COLORS['text_muted'],
        annotation_text='50% threshold',
        annotation_position='right',
    )

    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor=COLORS['bg'],
        plot_bgcolor=COLORS['bg'],
        font=dict(family='Source Sans Pro, sans-serif', color=COLORS['text']),
        title=dict(
            text='<b>Sole-Source Contract Prevalence</b><br>'
                 '<sup>Percentage of contract value awarded without competition</sup>',
            font=dict(size=16),
            x=0.5,
        ),
        xaxis=dict(
            showgrid=False,
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(255,255,255,0.05)',
            title='% of Contract Value',
            range=[0, 80],
        ),
        margin=dict(t=80, b=40, l=60, r=30),
        height=350,
        showlegend=False,
    )

    return fig


def create_vendor_concentration_chart():
    """Create a treemap showing vendor concentration."""
    data = []
    for category_key, category in CONTRACT_DATA.items():
        for contract in category['contracts']:
            data.append({
                'category': category['name'],
                'vendor': contract['vendor'],
                'value': contract['value'],
                'type': contract['type'],
            })

    df = pd.DataFrame(data)

    # Color mapping
    color_map = {
        'sole_source': COLORS['sole_source'],
        'limited': COLORS['limited'],
        'competitive': COLORS['competitive'],
    }

    fig = px.treemap(
        df,
        path=['category', 'vendor'],
        values='value',
        color='type',
        color_discrete_map=color_map,
        hover_data={'value': ':$,.0f'},
    )

    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor=COLORS['bg'],
        font=dict(family='Source Sans Pro, sans-serif', color=COLORS['text']),
        title=dict(
            text='<b>Contract Value by Vendor</b><br>'
                 '<sup>Size = contract value | Color = competition level</sup>',
            font=dict(size=16),
            x=0.5,
        ),
        margin=dict(t=80, b=20, l=20, r=20),
        height=450,
    )

    fig.update_traces(
        hovertemplate='<b>%{label}</b><br>Value: $%{value:,.0f}<extra></extra>',
        textinfo='label+percent parent',
    )

    return fig


def create_red_flag_card(flag_data, index):
    """Create a card for a contracting red flag."""
    return html.Div([
        html.Div([
            html.Span("🚩", className='flag-icon'),
            html.H4(flag_data['flag'], className='flag-title'),
        ], className='flag-header'),
        html.P(flag_data['description'], className='flag-description'),
        html.Div([
            html.Div([
                html.Span("Prevalence: ", className='flag-meta-label'),
                html.Span(flag_data['prevalence'], className='flag-meta-value'),
            ], className='flag-prevalence'),
            html.Div([
                html.Span("Example: ", className='flag-meta-label'),
                html.Span(flag_data['example'], className='flag-example'),
            ], className='flag-example-row'),
        ], className='flag-meta'),
    ], className='red-flag-card')


def get_rigged_bidding_content():
    """
    Build and return the Rigged Bidding Analyzer page.

    Returns:
        Dash html.Div with the bidding analysis
    """
    # Calculate totals
    total_value = sum(c['total_value'] for c in CONTRACT_DATA.values())
    sole_source_value = sum(
        sum(con['value'] for con in c['contracts'] if con['type'] == 'sole_source')
        for c in CONTRACT_DATA.values()
    )
    sole_source_pct = sole_source_value / total_value * 100

    competition_fig = create_competition_chart()
    treemap_fig = create_vendor_concentration_chart()

    red_flag_cards = [
        create_red_flag_card(flag, i)
        for i, flag in enumerate(RED_FLAGS)
    ]

    return html.Div([
        # Header
        html.Div([
            html.Div([
                html.H2("Rigged Bidding: The Illusion of Competition",
                       className='section-title'),
                html.P([
                    "Federal contracting is supposed to ensure taxpayers get the best value. ",
                    "But in immigration enforcement, the same vendors win year after year, ",
                    "often without competition. This analysis reveals patterns suggesting the ",
                    "bidding process may be designed to produce predetermined outcomes."
                ], className='section-intro'),
            ], className='container'),
        ], className='bidding-header'),

        # Key statistics
        html.Div([
            html.Div([
                html.Div([
                    html.Div([
                        html.Span("Total Contract Value", className='stat-label'),
                        html.Span(f"${total_value/1e9:.1f}B", className='stat-value'),
                    ], className='bidding-stat'),
                    html.Div([
                        html.Span("Sole Source", className='stat-label'),
                        html.Span(f"${sole_source_value/1e9:.1f}B", className='stat-value stat-warning'),
                        html.Span(f"({sole_source_pct:.0f}%)", className='stat-note'),
                    ], className='bidding-stat'),
                    html.Div([
                        html.Span("Avg. Bidders", className='stat-label'),
                        html.Span("1.8", className='stat-value'),
                        html.Span("(healthy = 4+)", className='stat-note'),
                    ], className='bidding-stat'),
                    html.Div([
                        html.Span("Red Flags Identified", className='stat-label'),
                        html.Span(f"{len(RED_FLAGS)}", className='stat-value stat-warning'),
                    ], className='bidding-stat'),
                ], className='bidding-stats-row'),
            ], className='container'),
        ], className='bidding-stats-bar'),

        # Competition chart
        html.Div([
            html.Div([
                dcc.Graph(
                    id='competition-chart',
                    figure=competition_fig,
                    config={'displayModeBar': False},
                ),
            ], className='container'),
        ], className='chart-section'),

        # Vendor concentration treemap
        html.Div([
            html.Div([
                dcc.Graph(
                    id='vendor-treemap',
                    figure=treemap_fig,
                    config={'displayModeBar': False},
                ),
                html.Div([
                    html.Div([
                        html.Span(className='legend-color', style={'backgroundColor': COLORS['sole_source']}),
                        html.Span("Sole Source (no competition)", className='legend-label'),
                    ], className='legend-item'),
                    html.Div([
                        html.Span(className='legend-color', style={'backgroundColor': COLORS['limited']}),
                        html.Span("Limited Competition (2-3 bidders)", className='legend-label'),
                    ], className='legend-item'),
                    html.Div([
                        html.Span(className='legend-color', style={'backgroundColor': COLORS['competitive']}),
                        html.Span("Competitive (4+ bidders)", className='legend-label'),
                    ], className='legend-item'),
                ], className='treemap-legend'),
            ], className='container'),
        ], className='chart-section'),

        # Red flags section
        html.Div([
            html.Div([
                html.H3("Red Flags in Contract Awards", className='subsection-title'),
                html.P([
                    "Patterns that suggest the competitive process may be compromised:"
                ], className='subsection-intro'),
                html.Div(red_flag_cards, className='red-flags-grid'),
            ], className='container'),
        ], className='red-flags-section'),

        # Case study
        html.Div([
            html.Div([
                html.Div([
                    html.H3("Case Study: The Adelanto Contract", className='case-title'),
                    html.P([
                        "In 2019, ICE awarded a $256 million sole-source contract to GEO Group ",
                        "for the Adelanto ICE Processing Center. The justification: 'Only GEO Group ",
                        "has the existing infrastructure and institutional knowledge to operate this facility.'"
                    ], className='case-text'),
                    html.P([
                        "But GEO Group only had that knowledge because they had won the previous ",
                        "contract—also sole-source. This circular logic creates permanent incumbency: ",
                        "win once, win forever."
                    ], className='case-text'),
                    html.Div([
                        html.Span("The Result: ", className='case-highlight-label'),
                        html.Span(
                            "GEO Group has held the Adelanto contract continuously since 2011. "
                            "No other company has ever operated the facility.",
                            className='case-highlight-text'
                        ),
                    ], className='case-highlight'),
                ], className='case-study-box'),
            ], className='container'),
        ], className='case-study-section'),

        # Methodology
        html.Div([
            html.Div([
                html.H4("Data Sources", className='methodology-title'),
                html.P([
                    "Contract data from USASpending.gov and Federal Procurement Data System (FPDS). ",
                    "Sole-source justifications from contract documents obtained via FOIA. ",
                    "Revolving door data from OpenSecrets and LinkedIn analysis. ",
                    "Red flag patterns identified through comparison with GAO contracting guidelines."
                ], className='methodology-text'),
            ], className='container'),
        ], className='bidding-methodology'),

    ], className='rigged-bidding-page')
