"""
Project Watchtower - Media Sentiment Pulse
FR 4.1: Track media coverage and sentiment around immigration enforcement

Visual Strategy: Real-time pulse visualization showing coverage volume
and sentiment trends, with breakdown by outlet type and topic.
"""

import plotly.graph_objects as go
from dash import html, dcc
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


# Color palette
COLORS = {
    'bg': '#0f0f23',
    'positive': '#06d6a0',
    'neutral': '#8d99ae',
    'negative': '#e53e3e',
    'text': '#e2e8f0',
    'text_muted': '#8d99ae',
}

# Sample media coverage data (in production, would be from news API)
def generate_sample_coverage():
    """Generate sample media coverage data for demonstration."""
    dates = pd.date_range(end=datetime.now(), periods=90, freq='D')

    coverage = []
    for date in dates:
        # Base coverage volume with some variation
        base_volume = 50 + np.random.normal(0, 15)

        # Simulate spikes around events
        if date.day % 15 == 0:  # Simulated "event" days
            base_volume *= 2.5

        coverage.append({
            'date': date,
            'volume': max(10, base_volume),
            'positive': np.random.randint(5, 20),
            'neutral': np.random.randint(20, 40),
            'negative': np.random.randint(30, 60),
        })

    return pd.DataFrame(coverage)


# Media outlet categories
OUTLET_CATEGORIES = {
    'mainstream': {
        'name': 'Mainstream Media',
        'outlets': ['NYT', 'WaPo', 'CNN', 'Fox News', 'NBC', 'ABC', 'CBS'],
        'sentiment_avg': -15,  # Slightly negative
        'coverage_pct': 45,
    },
    'local': {
        'name': 'Local News',
        'outlets': ['Local affiliates', 'Regional papers', 'City outlets'],
        'sentiment_avg': -8,
        'coverage_pct': 25,
    },
    'investigative': {
        'name': 'Investigative / Nonprofit',
        'outlets': ['ProPublica', 'The Marshall Project', 'TRAC', 'The Intercept'],
        'sentiment_avg': -45,  # More critical
        'coverage_pct': 10,
    },
    'advocacy': {
        'name': 'Advocacy Media',
        'outlets': ['ACLU', 'Human Rights Watch', 'RAICES'],
        'sentiment_avg': -65,
        'coverage_pct': 8,
    },
    'conservative': {
        'name': 'Conservative Media',
        'outlets': ['Breitbart', 'Daily Wire', 'Newsmax', 'OAN'],
        'sentiment_avg': 35,  # Pro-enforcement
        'coverage_pct': 12,
    },
}

# Top recent stories
RECENT_STORIES = [
    {
        'headline': 'ICE Arrests at Courthouse Spark Legal Challenge',
        'outlet': 'The Marshall Project',
        'date': '2024-01-15',
        'sentiment': 'negative',
        'topic': 'Enforcement',
    },
    {
        'headline': 'Detention Center Medical Care Under Scrutiny After Death',
        'outlet': 'ProPublica',
        'date': '2024-01-14',
        'sentiment': 'negative',
        'topic': 'Detention',
    },
    {
        'headline': 'Border Crossings Hit New Monthly Record',
        'outlet': 'Fox News',
        'date': '2024-01-13',
        'sentiment': 'negative',
        'topic': 'Border',
    },
    {
        'headline': 'Private Prison Company Reports Record Profits',
        'outlet': 'NYT',
        'date': '2024-01-12',
        'sentiment': 'neutral',
        'topic': 'Economics',
    },
    {
        'headline': 'Asylum Backlog Reaches 3 Million Cases',
        'outlet': 'CNN',
        'date': '2024-01-11',
        'sentiment': 'neutral',
        'topic': 'Legal',
    },
]


def create_sentiment_pulse():
    """Create the main sentiment pulse visualization."""
    df = generate_sample_coverage()

    fig = go.Figure()

    # Add sentiment area traces (stacked)
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['negative'],
        name='Critical Coverage',
        fill='tozeroy',
        fillcolor='rgba(229, 62, 62, 0.5)',
        line=dict(color=COLORS['negative'], width=0),
        hovertemplate='%{x|%b %d}<br>Critical: %{y}<extra></extra>',
    ))

    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['neutral'] + df['negative'],
        name='Neutral Coverage',
        fill='tonexty',
        fillcolor='rgba(141, 153, 174, 0.5)',
        line=dict(color=COLORS['neutral'], width=0),
        hovertemplate='%{x|%b %d}<br>Neutral: %{y}<extra></extra>',
    ))

    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['positive'] + df['neutral'] + df['negative'],
        name='Supportive Coverage',
        fill='tonexty',
        fillcolor='rgba(6, 214, 160, 0.5)',
        line=dict(color=COLORS['positive'], width=0),
        hovertemplate='%{x|%b %d}<br>Supportive: %{y}<extra></extra>',
    ))

    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor=COLORS['bg'],
        plot_bgcolor=COLORS['bg'],
        font=dict(family='Source Sans Pro, sans-serif', color=COLORS['text']),
        title=dict(
            text='<b>Media Coverage Pulse</b><br>'
                 '<sup>90-day sentiment breakdown by coverage type</sup>',
            font=dict(size=18),
            x=0.5,
        ),
        xaxis=dict(
            showgrid=False,
            title='',
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(255,255,255,0.05)',
            title='Daily Articles',
        ),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=-0.15,
            xanchor='center',
            x=0.5,
        ),
        margin=dict(t=80, b=60, l=60, r=30),
        height=400,
        hovermode='x unified',
    )

    return fig


def create_outlet_breakdown():
    """Create breakdown by outlet category."""
    categories = list(OUTLET_CATEGORIES.keys())
    names = [OUTLET_CATEGORIES[c]['name'] for c in categories]
    coverage = [OUTLET_CATEGORIES[c]['coverage_pct'] for c in categories]
    sentiment = [OUTLET_CATEGORIES[c]['sentiment_avg'] for c in categories]

    # Color based on sentiment
    colors = [
        COLORS['positive'] if s > 0 else COLORS['negative']
        for s in sentiment
    ]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=names,
        y=coverage,
        marker_color=colors,
        text=[f'{c}%' for c in coverage],
        textposition='outside',
        hovertemplate='%{x}<br>Coverage: %{y}%<br>Sentiment: %{customdata:+d}<extra></extra>',
        customdata=sentiment,
    ))

    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor=COLORS['bg'],
        plot_bgcolor=COLORS['bg'],
        font=dict(family='Source Sans Pro, sans-serif', color=COLORS['text']),
        title=dict(
            text='<b>Coverage by Outlet Type</b>',
            font=dict(size=14),
        ),
        xaxis=dict(showgrid=False, tickangle=45),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(255,255,255,0.05)',
            title='% of Total Coverage',
        ),
        margin=dict(t=60, b=80, l=60, r=30),
        height=300,
        showlegend=False,
    )

    return fig


def create_story_card(story):
    """Create a card for a recent story."""
    sentiment_colors = {
        'positive': COLORS['positive'],
        'neutral': COLORS['neutral'],
        'negative': COLORS['negative'],
    }

    return html.Div([
        html.Div([
            html.Span(story['outlet'], className='story-outlet'),
            html.Span(story['date'], className='story-date'),
        ], className='story-meta'),
        html.H4(story['headline'], className='story-headline'),
        html.Div([
            html.Span(
                story['sentiment'].title(),
                className='story-sentiment',
                style={'color': sentiment_colors[story['sentiment']]}
            ),
            html.Span(story['topic'], className='story-topic'),
        ], className='story-tags'),
    ], className='story-card')


def get_media_pulse_content():
    """
    Build and return the Media Sentiment Pulse page.

    Returns:
        Dash html.Div with the media analysis
    """
    pulse_fig = create_sentiment_pulse()
    outlet_fig = create_outlet_breakdown()

    story_cards = [create_story_card(story) for story in RECENT_STORIES]

    return html.Div([
        # Header
        html.Div([
            html.Div([
                html.H2("Media Sentiment Pulse", className='section-title'),
                html.P([
                    "How is immigration enforcement covered in the media? This dashboard ",
                    "tracks coverage volume and sentiment across different outlet types, ",
                    "revealing patterns in how the story is told—and by whom."
                ], className='section-intro'),
            ], className='container'),
        ], className='pulse-header'),

        # Key metrics
        html.Div([
            html.Div([
                html.Div([
                    html.Div([
                        html.Span("Avg Daily Articles", className='stat-label'),
                        html.Span("127", className='stat-value'),
                    ], className='pulse-stat'),
                    html.Div([
                        html.Span("Overall Sentiment", className='stat-label'),
                        html.Span("-18", className='stat-value stat-negative'),
                        html.Span("(net negative)", className='stat-note'),
                    ], className='pulse-stat'),
                    html.Div([
                        html.Span("Coverage Trend", className='stat-label'),
                        html.Span("+23%", className='stat-value stat-warning'),
                        html.Span("vs. last month", className='stat-note'),
                    ], className='pulse-stat'),
                    html.Div([
                        html.Span("Top Topic", className='stat-label'),
                        html.Span("Border", className='stat-value'),
                    ], className='pulse-stat'),
                ], className='pulse-stats-row'),
            ], className='container'),
        ], className='pulse-stats-bar'),

        # Main pulse visualization
        html.Div([
            html.Div([
                dcc.Graph(
                    id='sentiment-pulse',
                    figure=pulse_fig,
                    config={'displayModeBar': False},
                ),
            ], className='container'),
        ], className='pulse-chart-section'),

        # Two-column: outlet breakdown + recent stories
        html.Div([
            html.Div([
                html.Div([
                    html.Div([
                        dcc.Graph(
                            id='outlet-breakdown',
                            figure=outlet_fig,
                            config={'displayModeBar': False},
                        ),
                    ], className='outlet-chart'),
                    html.Div([
                        html.H3("Recent Coverage", className='subsection-title'),
                        html.Div(story_cards, className='stories-list'),
                    ], className='stories-section'),
                ], className='pulse-grid'),
            ], className='container'),
        ], className='analysis-section'),

        # Methodology
        html.Div([
            html.Div([
                html.H4("Methodology", className='methodology-title'),
                html.P([
                    "Sentiment analysis uses NLP models trained on immigration-specific coverage. ",
                    "Scores range from -100 (highly critical of enforcement) to +100 (highly supportive). ",
                    "Coverage tracked from major news outlets, local media, investigative nonprofits, ",
                    "and advocacy organizations. Data updated daily."
                ], className='methodology-text'),
                html.P([
                    html.Strong("Note: "),
                    "Sample data shown for demonstration. Production version would integrate ",
                    "with news APIs (GDELT, NewsAPI, MediaCloud) for real-time tracking."
                ], style={'color': '#ed8936', 'fontSize': '0.85rem', 'marginTop': '10px'}),
            ], className='container'),
        ], className='pulse-methodology'),

    ], className='media-pulse-page')
