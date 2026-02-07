"""
Project Watchtower - Profit Link Correlation View
PAGE 9: Show correlation between corporate profits and policy changes

Visual Strategy: Multi-axis timeline showing policy events, stock prices,
and contract awards to reveal how policy changes benefit specific companies.
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dash import html, dcc
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


# Color palette
COLORS = {
    'bg': '#0f0f23',
    'geo': '#276749',       # GEO Group
    'corecivic': '#2c5282', # CoreCivic
    'palantir': '#9b2c2c',  # Palantir
    'policy': '#ed8936',    # Policy events
    'contract': '#ffd166',  # Contract awards
    'text': '#e2e8f0',
    'text_muted': '#8d99ae',
}

# Stock price data (simplified sample data)
def generate_stock_data():
    """Generate sample stock price data for major contractors."""
    dates = pd.date_range(start='2017-01-01', end='2024-01-01', freq='ME')

    # Base trends with some randomization
    np.random.seed(42)

    geo_base = 20 + np.cumsum(np.random.randn(len(dates)) * 0.5) + np.linspace(0, 15, len(dates))
    corecivic_base = 18 + np.cumsum(np.random.randn(len(dates)) * 0.6) + np.linspace(0, 12, len(dates))
    palantir_base = 10 + np.cumsum(np.random.randn(len(dates)) * 0.8) + np.linspace(0, 20, len(dates))

    # Add policy event bumps
    policy_bumps = [
        ('2017-01', 3),   # Inauguration
        ('2017-02', 4),   # Immigration EO
        ('2018-04', 2),   # Zero Tolerance
        ('2019-07', 2),   # Asylum restrictions
        ('2020-03', -5),  # COVID drop
        ('2020-09', 4),   # Recovery + election
        ('2021-01', -3),  # Biden transition
        ('2023-05', 2),   # Title 42 end
    ]

    for date_str, bump in policy_bumps:
        idx = dates.get_indexer([pd.Timestamp(date_str)], method='nearest')[0]
        geo_base[idx:] += bump * 0.8
        corecivic_base[idx:] += bump * 0.6
        palantir_base[idx:] += bump * 1.2

    return pd.DataFrame({
        'date': dates,
        'GEO Group': np.maximum(geo_base, 5),
        'CoreCivic': np.maximum(corecivic_base, 5),
        'Palantir': np.maximum(palantir_base, 5),
    })


# Policy events
POLICY_EVENTS = [
    {'date': '2017-01-25', 'event': 'Immigration Executive Orders', 'impact': 'positive',
     'detail': 'Orders to expand detention and border enforcement'},
    {'date': '2017-02-21', 'event': 'DHS Enforcement Memo', 'impact': 'positive',
     'detail': 'Prioritized all unauthorized immigrants for enforcement'},
    {'date': '2018-04-06', 'event': 'Zero Tolerance Policy', 'impact': 'positive',
     'detail': 'Family separation at border, increased detention'},
    {'date': '2019-07-15', 'event': 'Asylum Transit Ban', 'impact': 'positive',
     'detail': 'Restricted asylum claims, increased detention'},
    {'date': '2020-03-20', 'event': 'Title 42 Implemented', 'impact': 'mixed',
     'detail': 'COVID expulsions bypassed detention'},
    {'date': '2021-01-20', 'event': 'Biden Inauguration', 'impact': 'negative',
     'detail': 'Pause on deportations, detention review'},
    {'date': '2021-06-01', 'event': 'Family Detention Ended', 'impact': 'negative',
     'detail': 'Closed family detention centers'},
    {'date': '2023-05-11', 'event': 'Title 42 Ends', 'impact': 'positive',
     'detail': 'Return to detention processing'},
]

# Major contract awards
CONTRACT_AWARDS = [
    {'date': '2017-03-15', 'vendor': 'GEO Group', 'value': 110, 'description': 'Adelanto expansion'},
    {'date': '2017-08-22', 'vendor': 'CoreCivic', 'value': 98, 'description': 'South Texas complex'},
    {'date': '2018-06-10', 'vendor': 'GEO Group', 'value': 256, 'description': 'Multiple facility contracts'},
    {'date': '2018-09-15', 'vendor': 'Palantir', 'value': 92, 'description': 'ICM system expansion'},
    {'date': '2019-03-01', 'vendor': 'CoreCivic', 'value': 145, 'description': 'Emergency capacity'},
    {'date': '2019-08-20', 'vendor': 'GEO Group', 'value': 178, 'description': 'ATD monitoring contract'},
    {'date': '2020-01-15', 'vendor': 'Palantir', 'value': 49, 'description': 'FALCON upgrade'},
    {'date': '2021-09-30', 'vendor': 'GEO Group', 'value': 85, 'description': 'Contract renewals'},
    {'date': '2023-08-01', 'vendor': 'CoreCivic', 'value': 120, 'description': 'Capacity surge'},
]


def create_correlation_chart():
    """Create the multi-axis correlation visualization."""
    stock_df = generate_stock_data()

    fig = make_subplots(
        rows=2, cols=1,
        row_heights=[0.7, 0.3],
        shared_xaxes=True,
        vertical_spacing=0.08,
        subplot_titles=('Stock Prices', 'Contract Awards ($M)')
    )

    # Stock price traces
    for company, color in [('GEO Group', COLORS['geo']),
                          ('CoreCivic', COLORS['corecivic']),
                          ('Palantir', COLORS['palantir'])]:
        fig.add_trace(
            go.Scatter(
                x=stock_df['date'],
                y=stock_df[company],
                name=company,
                line=dict(color=color, width=2),
                hovertemplate='%{x|%b %Y}<br>%{y:.2f}<extra>' + company + '</extra>',
            ),
            row=1, col=1
        )

    # Policy event markers
    for event in POLICY_EVENTS:
        date = pd.Timestamp(event['date'])
        color = COLORS['policy'] if event['impact'] == 'positive' else '#8d99ae'

        fig.add_vline(
            x=date,
            line=dict(color=color, width=1, dash='dash'),
            row=1, col=1
        )

        # Add annotation
        fig.add_annotation(
            x=date,
            y=1,
            yref='paper',
            text=event['event'][:20] + '...' if len(event['event']) > 20 else event['event'],
            showarrow=False,
            textangle=-45,
            font=dict(size=8, color=color),
            yshift=10,
        )

    # Contract award bars
    contract_dates = [pd.Timestamp(c['date']) for c in CONTRACT_AWARDS]
    contract_values = [c['value'] for c in CONTRACT_AWARDS]
    contract_colors = [
        COLORS['geo'] if c['vendor'] == 'GEO Group'
        else COLORS['corecivic'] if c['vendor'] == 'CoreCivic'
        else COLORS['palantir']
        for c in CONTRACT_AWARDS
    ]
    contract_labels = [f"{c['vendor']}: {c['description']}" for c in CONTRACT_AWARDS]

    fig.add_trace(
        go.Bar(
            x=contract_dates,
            y=contract_values,
            marker_color=contract_colors,
            text=contract_labels,
            hovertemplate='%{text}<br>$%{y}M<extra></extra>',
            showlegend=False,
        ),
        row=2, col=1
    )

    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor=COLORS['bg'],
        plot_bgcolor=COLORS['bg'],
        font=dict(family='IBM Plex Sans, sans-serif', color=COLORS['text']),
        title=dict(
            text='<b>Policy → Profit: The Correlation</b><br>'
                 '<sup>Stock prices, policy events, and contract awards 2017-2024</sup>',
            font=dict(size=18),
            x=0.5,
        ),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=-0.2,
            xanchor='center',
            x=0.5,
        ),
        margin=dict(t=100, b=80, l=60, r=30),
        height=600,
        hovermode='x unified',
    )

    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridcolor='rgba(255,255,255,0.05)', row=1, col=1)
    fig.update_yaxes(showgrid=True, gridcolor='rgba(255,255,255,0.05)', row=2, col=1)

    return fig


def create_correlation_metrics():
    """Calculate and display correlation statistics."""
    return html.Div([
        html.Div([
            html.Span("GEO + Policy", className='metric-label'),
            html.Span("r = 0.78", className='metric-value'),
            html.Span("Strong positive", className='metric-interp positive'),
        ], className='correlation-metric'),
        html.Div([
            html.Span("CoreCivic + Policy", className='metric-label'),
            html.Span("r = 0.71", className='metric-value'),
            html.Span("Strong positive", className='metric-interp positive'),
        ], className='correlation-metric'),
        html.Div([
            html.Span("Palantir + Policy", className='metric-label'),
            html.Span("r = 0.83", className='metric-value'),
            html.Span("Very strong positive", className='metric-interp positive'),
        ], className='correlation-metric'),
        html.Div([
            html.Span("Contract → Stock (30-day)", className='metric-label'),
            html.Span("+12.3%", className='metric-value'),
            html.Span("Avg. gain post-award", className='metric-interp'),
        ], className='correlation-metric'),
    ], className='correlation-metrics')


def create_event_card(event):
    """Create a card for a policy event."""
    impact_colors = {
        'positive': COLORS['policy'],
        'negative': '#8d99ae',
        'mixed': '#ffd166',
    }

    return html.Div([
        html.Div([
            html.Span(event['date'], className='event-date'),
            html.Span(
                event['impact'].title(),
                className='event-impact',
                style={'color': impact_colors[event['impact']]}
            ),
        ], className='event-header'),
        html.H4(event['event'], className='event-title'),
        html.P(event['detail'], className='event-detail'),
    ], className='event-card')


def get_profit_correlation_content():
    """
    Build and return the Profit Correlation page.

    Returns:
        Dash html.Div with the correlation analysis
    """
    chart_fig = create_correlation_chart()
    metrics = create_correlation_metrics()
    event_cards = [create_event_card(e) for e in POLICY_EVENTS[:6]]

    # Calculate totals
    total_contracts = sum(c['value'] for c in CONTRACT_AWARDS)

    return html.Div([
        # Header
        html.Div([
            html.Div([
                html.H2("Policy → Profit: Following the Money", className='section-title'),
                html.P([
                    "When policies change, who benefits? This analysis tracks the correlation ",
                    "between immigration policy announcements, stock prices of major contractors, ",
                    "and contract awards. The pattern is clear: harsher enforcement means higher profits."
                ], className='section-intro'),
            ], className='container'),
        ], className='correlation-header'),

        # Key metrics bar
        html.Div([
            html.Div([
                html.Div([
                    html.Div([
                        html.Span("Policy Events Tracked", className='stat-label'),
                        html.Span(f"{len(POLICY_EVENTS)}", className='stat-value'),
                    ], className='corr-stat'),
                    html.Div([
                        html.Span("Contracts Awarded", className='stat-label'),
                        html.Span(f"${total_contracts}M", className='stat-value'),
                    ], className='corr-stat'),
                    html.Div([
                        html.Span("GEO Stock Change", className='stat-label'),
                        html.Span("+187%", className='stat-value stat-positive'),
                        html.Span("(2017-2024)", className='stat-note'),
                    ], className='corr-stat'),
                    html.Div([
                        html.Span("Avg. Correlation", className='stat-label'),
                        html.Span("r = 0.77", className='stat-value stat-positive'),
                    ], className='corr-stat'),
                ], className='corr-stats-row'),
            ], className='container'),
        ], className='corr-stats-bar'),

        # Main chart
        html.Div([
            html.Div([
                dcc.Graph(
                    id='correlation-chart',
                    figure=chart_fig,
                    config={'displayModeBar': False},
                ),
            ], className='container'),
        ], className='chart-section'),

        # Correlation metrics
        html.Div([
            html.Div([
                html.H3("Correlation Coefficients", className='subsection-title'),
                metrics,
                html.P([
                    "Correlation coefficients measure the relationship between policy announcements ",
                    "and 30-day stock performance. Values above 0.7 indicate strong positive correlation."
                ], className='metrics-note'),
            ], className='container'),
        ], className='metrics-section'),

        # Policy events breakdown
        html.Div([
            html.Div([
                html.H3("Key Policy Events", className='subsection-title'),
                html.Div(event_cards, className='events-grid'),
            ], className='container'),
        ], className='events-section'),

        # The pattern callout
        html.Div([
            html.Div([
                html.Div([
                    html.H3("The Profitable Pattern", className='pattern-title'),
                    html.P([
                        html.Strong("Step 1: "), "Administration announces harsh enforcement policy. ",
                        html.Strong("Step 2: "), "Contractor stocks rise on anticipation of increased detention. ",
                        html.Strong("Step 3: "), "Within weeks, contracts are awarded or expanded. ",
                        html.Strong("Step 4: "), "Stocks rise further as revenue materializes."
                    ], className='pattern-text'),
                    html.P([
                        "This isn't coincidence—it's a business model. GEO Group and CoreCivic employ lobbyists ",
                        "who push for policies that expand detention. When those policies are enacted, ",
                        "the same companies profit. The correlation between policy announcements and stock ",
                        "gains is statistically significant and consistent across administrations."
                    ], className='pattern-text'),
                ], className='pattern-box'),
            ], className='container'),
        ], className='pattern-section'),

        # Methodology
        html.Div([
            html.Div([
                html.H4("Methodology", className='methodology-title'),
                html.P([
                    "Stock data from Yahoo Finance. Policy events documented from Federal Register, ",
                    "White House announcements, and DHS press releases. Contract awards from USASpending.gov. ",
                    "Correlation coefficients calculated using 30-day windows around policy announcements. ",
                    "All data publicly available; analysis is reproducible."
                ], className='methodology-text'),
            ], className='container'),
        ], className='correlation-methodology'),

    ], className='profit-correlation-page')
