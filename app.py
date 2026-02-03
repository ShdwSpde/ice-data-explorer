"""
ICE Data Explorer - Interactive Dashboard
A journalism-style data exploration tool for immigration enforcement data
"""

import dash
from dash import dcc, html, Input, Output, State, callback, dash_table, clientside_callback
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import sqlite3
import os
from datetime import datetime
from database import init_database, seed_data, query_data, execute_query, DB_PATH
from pages.narratives import get_criminality_myth_content, get_detention_cartogram_content, get_isotype_timeline_content
from pages.taxpayer_receipt import get_taxpayer_receipt_content, generate_receipt_html, generate_opportunity_costs, calculate_tax_contribution
from pages.surveillance import get_surveillance_tracker_content
from pages.logistics_map import get_logistics_map_content
from pages.memorial import get_memorial_content
from pages.deportation_globe import get_deportation_globe_content
from pages.economic_sankey import get_economic_sankey_content
from pages.landing import get_landing_content, REVEAL_JS, LIFT_ALL_JS
from pages.abuse_archive import get_abuse_archive_content
from pages.rigged_bidding import get_rigged_bidding_content
from pages.arrest_heatmap import get_arrest_heatmap_content
from pages.corporate_hydra import get_corporate_hydra_content
from pages.media_pulse import get_media_pulse_content
from pages.data_gaps import get_data_gaps_content
from pages.profit_correlation import get_profit_correlation_content
from pages.community_resources import get_community_resources_content
from analysis.bayesian import get_bayesian_analysis_content
from components.share import create_share_button, create_alert_share_widget, generate_telegram_url, generate_whatsapp_url, generate_email_url, SHARE_JS

# Initialize database if needed
if not os.path.exists(DB_PATH):
    init_database()
    seed_data()

# Initialize Dash app with Bootstrap theme
app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        'https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700;900&family=Source+Sans+Pro:wght@300;400;600;700&display=swap'
    ],
    suppress_callback_exceptions=True,
    title="The Cost of Enforcement | ICE Data Explorer"
)

server = app.server

# Color palette (journalism/documentary style)
COLORS = {
    'primary': '#1a1a2e',
    'secondary': '#16213e',
    'accent': '#e94560',
    'accent_light': '#ff6b6b',
    'text': '#edf2f4',
    'text_muted': '#8d99ae',
    'chart_bg': '#0f0f23',
    'grid': '#2b2d42',
    'success': '#06d6a0',
    'warning': '#ffd166',
    'danger': '#ef476f',
    'blue': '#118ab2',
    'purple': '#7209b7',
}

# ============================================
# DATA EXPLORER CONFIGURATION
# ============================================

# Dataset descriptions for context
DATASET_DESCRIPTIONS = {
    'agency_budgets': 'Historical budget data for Border Patrol, ICE, and CBP from 1994-2024, showing both nominal and inflation-adjusted figures.',
    'budget_allocations_2025': 'Breakdown of the $170 billion 2025 immigration enforcement budget by category.',
    'detention_population': 'Monthly ICE detention population figures from 2014-2026, including criminal record breakdowns.',
    'detention_by_state': 'State-level detention statistics including facility counts.',
    'deportations': 'Annual deportation (removal) statistics by fiscal year from 2008-2025.',
    'deportations_by_nationality': 'Deportation figures broken down by country of origin.',
    'deaths_in_custody': 'Annual deaths in ICE custody from 2004-2025.',
    'abuse_complaints': 'Documented abuse categories and complaints in detention facilities.',
    'deportation_costs': 'Cost estimates for deportations from various sources including ICE and Penn Wharton.',
    'private_prison_contracts': 'Annual revenue figures for GEO Group and CoreCivic from ICE contracts.',
    'staffing': 'Agency employment figures over time.',
    'arrests': 'Monthly ICE arrest statistics.',
    'arrests_by_state': 'ICE arrest rates per 100,000 residents by state.',
    'detainee_criminal_status': 'Breakdown of detainees by criminal conviction status.',
    'key_statistics': 'Curated key statistics and metrics with source citations.',
    'news_articles': 'News coverage timeline with sentiment analysis scores.',
}

# Columns to hide from display (internal/not useful)
HIDDEN_COLUMNS = ['id', 'impact_score']

# Human-readable column name mappings
COLUMN_LABELS = {
    'id': 'ID',
    'year': 'Year',
    'month': 'Month',
    'date': 'Date',
    'agency': 'Agency',
    'budget_millions': 'Budget ($M)',
    'budget_adjusted_millions': 'Budget Adjusted ($M)',
    'notes': 'Notes',
    'source': 'Source',
    'category': 'Category',
    'amount_billions': 'Amount ($B)',
    'description': 'Description',
    'population': 'Population',
    'with_criminal_record': 'With Criminal Record',
    'without_criminal_record': 'Without Criminal Record',
    'pending_charges': 'Pending Charges',
    'state': 'State',
    'facilities_count': 'Facilities',
    'fiscal_year': 'Fiscal Year',
    'removals': 'Removals',
    'returns': 'Returns',
    'total': 'Total',
    'nationality': 'Nationality',
    'count': 'Count',
    'percentage': 'Percentage',
    'deaths': 'Deaths',
    'preventable_percentage': 'Preventable %',
    'cost_type': 'Cost Type',
    'amount_dollars': 'Amount ($)',
    'company': 'Company',
    'revenue_millions': 'Revenue ($M)',
    'employees': 'Employees',
    'arrests': 'Arrests',
    'daily_average': 'Daily Average',
    'arrests_per_100k': 'Arrests per 100K',
    'total_arrests': 'Total Arrests',
    'no_convictions_pct': 'No Convictions %',
    'violent_convictions_pct': 'Violent Convictions %',
    'nonviolent_convictions_pct': 'Non-Violent Convictions %',
    'pending_charges_pct': 'Pending Charges %',
    'metric': 'Metric',
    'value': 'Value',
    'context': 'Context',
    'impact_score': 'Impact Score',
    'headline': 'Headline',
    'url': 'URL',
    'sentiment_score': 'Sentiment Score',
    'sentiment_label': 'Sentiment',
    'summary': 'Summary',
    'image_url': 'Image URL',
}

# Currency columns that need $ formatting
CURRENCY_COLUMNS = ['budget_millions', 'budget_adjusted_millions', 'amount_billions',
                    'amount_dollars', 'revenue_millions']

# Large number columns that need comma formatting
NUMBER_COLUMNS = ['population', 'with_criminal_record', 'without_criminal_record',
                  'pending_charges', 'removals', 'returns', 'total', 'count',
                  'deaths', 'employees', 'arrests', 'total_arrests', 'facilities_count']

# Percentage columns
PERCENTAGE_COLUMNS = ['percentage', 'preventable_percentage', 'no_convictions_pct',
                      'violent_convictions_pct', 'nonviolent_convictions_pct', 'pending_charges_pct']


def format_value(value, column_name):
    """Format a value based on its column type."""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return '—'

    if column_name in CURRENCY_COLUMNS:
        if isinstance(value, (int, float)):
            if abs(value) >= 1_000_000_000:
                return f'${value/1_000_000_000:,.2f}B'
            elif abs(value) >= 1_000_000:
                return f'${value/1_000_000:,.2f}M'
            elif abs(value) >= 1_000:
                return f'${value:,.0f}'
            else:
                return f'${value:,.2f}'

    if column_name in NUMBER_COLUMNS:
        if isinstance(value, (int, float)):
            return f'{value:,.0f}'

    if column_name in PERCENTAGE_COLUMNS:
        if isinstance(value, (int, float)):
            return f'{value:.1f}%'

    return value


def get_column_label(column_name):
    """Get human-readable label for a column."""
    return COLUMN_LABELS.get(column_name, column_name.replace('_', ' ').title())


def get_available_years(table_name):
    """Get list of years available in a table."""
    year_column = 'year' if table_name != 'deportations' else 'fiscal_year'

    try:
        if table_name in ['agency_budgets', 'detention_population', 'detention_by_state',
                          'deportations', 'deportations_by_nationality', 'deaths_in_custody',
                          'abuse_complaints', 'private_prison_contracts', 'staffing',
                          'arrests', 'arrests_by_state', 'detainee_criminal_status', 'key_statistics']:
            col = 'fiscal_year' if table_name in ['deportations', 'deportations_by_nationality'] else 'year'
            data = query_data(f'SELECT DISTINCT {col} FROM {table_name} WHERE {col} IS NOT NULL ORDER BY {col} DESC')
            return [row[col] for row in data if row[col] is not None]
    except:
        pass
    return []


def calculate_summary_stats(df, numeric_cols):
    """Calculate summary statistics for numeric columns."""
    stats = {}
    for col in numeric_cols:
        if col in df.columns and col not in HIDDEN_COLUMNS:
            try:
                series = pd.to_numeric(df[col], errors='coerce').dropna()
                if len(series) > 0:
                    stats[col] = {
                        'min': series.min(),
                        'max': series.max(),
                        'avg': series.mean(),
                        'sum': series.sum(),
                        'count': len(series)
                    }
            except:
                pass
    return stats


def create_key_stat_card(value, label, subtext=None, color=COLORS['accent']):
    """Create a visually striking statistic card."""
    return dbc.Card([
        dbc.CardBody([
            html.H2(value, className='stat-value', style={'color': color}),
            html.P(label, className='stat-label'),
            html.Small(subtext, className='stat-subtext') if subtext else None,
        ], className='text-center')
    ], className='stat-card')


def get_budget_chart():
    """Create historical budget comparison chart."""
    data = query_data('''
        SELECT year, agency, budget_millions, budget_adjusted_millions
        FROM agency_budgets
        WHERE agency IN ('ICE', 'Border Patrol', 'CBP')
        ORDER BY year
    ''')
    df = pd.DataFrame(data)

    fig = go.Figure()

    for agency in ['Border Patrol', 'ICE', 'CBP']:
        agency_df = df[df['agency'] == agency]
        fig.add_trace(go.Scatter(
            x=agency_df['year'],
            y=agency_df['budget_adjusted_millions'],
            name=agency,
            mode='lines+markers',
            line=dict(width=3),
            marker=dict(size=8),
            hovertemplate='<b>%{x}</b><br>' +
                          f'{agency}: $%{{y:,.0f}}M<br>' +
                          '<extra></extra>'
        ))

    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor=COLORS['chart_bg'],
        plot_bgcolor=COLORS['chart_bg'],
        font=dict(family='Source Sans Pro', color=COLORS['text']),
        title=dict(
            text='<b>Immigration Enforcement Budget Growth</b><br><sup>Inflation-Adjusted (Millions USD)</sup>',
            font=dict(size=20)
        ),
        xaxis=dict(
            title='Fiscal Year',
            gridcolor=COLORS['grid'],
            showgrid=True
        ),
        yaxis=dict(
            title='Budget (Millions USD)',
            gridcolor=COLORS['grid'],
            showgrid=True,
            tickformat='$,.0f'
        ),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='center',
            x=0.5
        ),
        hovermode='x unified',
        margin=dict(t=100)
    )

    return fig


def get_detention_population_chart():
    """Create detention population timeline."""
    data = query_data('''
        SELECT date, year, population
        FROM detention_population
        ORDER BY date
    ''')
    df = pd.DataFrame(data)
    df['date'] = pd.to_datetime(df['date'])

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['population'],
        mode='lines+markers',
        fill='tozeroy',
        line=dict(color=COLORS['accent'], width=3),
        marker=dict(size=10, color=COLORS['accent']),
        fillcolor='rgba(233, 69, 96, 0.2)',
        hovertemplate='<b>%{x|%B %Y}</b><br>Population: %{y:,}<extra></extra>'
    ))

    # Add key event annotations
    events = [
        ('2020-03-01', 'COVID-19 Pandemic', 38000),
        ('2025-01-20', 'Trump 2nd Term Begins', 40000),
        ('2025-07-01', '$170B Bill Passed', 58000),
        ('2026-01-15', 'Record: 73,000', 73000),
    ]

    for date, text, y in events:
        fig.add_annotation(
            x=date,
            y=y,
            text=text,
            showarrow=True,
            arrowhead=2,
            arrowcolor=COLORS['text_muted'],
            font=dict(size=10, color=COLORS['text_muted']),
            bgcolor=COLORS['secondary'],
            borderpad=4,
            ax=0,
            ay=-40
        )

    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor=COLORS['chart_bg'],
        plot_bgcolor=COLORS['chart_bg'],
        font=dict(family='Source Sans Pro', color=COLORS['text']),
        title=dict(
            text='<b>ICE Detention Population Over Time</b><br><sup>Record highs reached in 2025-2026</sup>',
            font=dict(size=20)
        ),
        xaxis=dict(
            title='',
            gridcolor=COLORS['grid'],
            showgrid=True
        ),
        yaxis=dict(
            title='People Detained',
            gridcolor=COLORS['grid'],
            showgrid=True,
            tickformat=','
        ),
        showlegend=False,
        margin=dict(t=100)
    )

    return fig


def get_deaths_chart():
    """Create deaths in custody chart."""
    data = query_data('SELECT year, deaths FROM deaths_in_custody ORDER BY year')
    df = pd.DataFrame(data)

    colors = [COLORS['danger'] if y == 2025 else COLORS['text_muted'] for y in df['year']]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=df['year'],
        y=df['deaths'],
        marker_color=colors,
        text=df['deaths'],
        textposition='outside',
        textfont=dict(color=COLORS['text'], size=14, family='Source Sans Pro'),
        hovertemplate='<b>%{x}</b><br>Deaths: %{y}<extra></extra>'
    ))

    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor=COLORS['chart_bg'],
        plot_bgcolor=COLORS['chart_bg'],
        font=dict(family='Source Sans Pro', color=COLORS['text']),
        title=dict(
            text='<b>Deaths in ICE Custody</b><br><sup>2025: Deadliest year in two decades</sup>',
            font=dict(size=20)
        ),
        xaxis=dict(
            title='Year',
            gridcolor=COLORS['grid'],
            showgrid=False,
            tickmode='linear'
        ),
        yaxis=dict(
            title='Number of Deaths',
            gridcolor=COLORS['grid'],
            showgrid=True,
            range=[0, 40]
        ),
        showlegend=False,
        margin=dict(t=100)
    )

    return fig


def get_criminal_status_chart():
    """Create detainee criminal status chart."""
    fig = go.Figure()

    fig.add_trace(go.Pie(
        labels=['No Criminal Convictions', 'Violent Convictions', 'Non-Violent Convictions'],
        values=[73, 5, 22],
        hole=0.6,
        marker=dict(colors=[COLORS['accent'], COLORS['danger'], COLORS['warning']]),
        textinfo='label+percent',
        textposition='outside',
        textfont=dict(size=12, color=COLORS['text']),
        hovertemplate='<b>%{label}</b><br>%{percent}<extra></extra>'
    ))

    fig.add_annotation(
        text='<b>73%</b><br>No Criminal<br>Record',
        x=0.5, y=0.5,
        font=dict(size=18, color=COLORS['accent'], family='Playfair Display'),
        showarrow=False
    )

    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor=COLORS['chart_bg'],
        plot_bgcolor=COLORS['chart_bg'],
        font=dict(family='Source Sans Pro', color=COLORS['text']),
        title=dict(
            text='<b>Who Is Being Detained?</b><br><sup>Criminal conviction status of ICE detainees (2025)</sup>',
            font=dict(size=20)
        ),
        showlegend=False,
        margin=dict(t=100)
    )

    return fig


def get_deportations_chart():
    """Create deportations over time chart."""
    data = query_data('SELECT fiscal_year, removals, total FROM deportations ORDER BY fiscal_year')
    df = pd.DataFrame(data)

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=df['fiscal_year'],
        y=df['removals'],
        name='Formal Removals',
        marker_color=COLORS['blue'],
        hovertemplate='<b>FY %{x}</b><br>Removals: %{y:,}<extra></extra>'
    ))

    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor=COLORS['chart_bg'],
        plot_bgcolor=COLORS['chart_bg'],
        font=dict(family='Source Sans Pro', color=COLORS['text']),
        title=dict(
            text='<b>Annual Deportations</b><br><sup>Formal removals by fiscal year</sup>',
            font=dict(size=20)
        ),
        xaxis=dict(
            title='Fiscal Year',
            gridcolor=COLORS['grid'],
            showgrid=False,
            tickmode='linear',
            dtick=2
        ),
        yaxis=dict(
            title='Number of Deportations',
            gridcolor=COLORS['grid'],
            showgrid=True,
            tickformat=','
        ),
        showlegend=False,
        margin=dict(t=100)
    )

    return fig


def get_private_prison_chart():
    """Create private prison revenue chart."""
    data = query_data('''
        SELECT year, company, revenue_millions
        FROM private_prison_contracts
        ORDER BY year, company
    ''')
    df = pd.DataFrame(data)

    fig = go.Figure()

    for company in ['GEO Group', 'CoreCivic']:
        company_df = df[df['company'] == company]
        fig.add_trace(go.Bar(
            x=company_df['year'],
            y=company_df['revenue_millions'],
            name=company,
            hovertemplate='<b>%{x}</b><br>' + company + ': $%{y:,.0f}M<extra></extra>'
        ))

    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor=COLORS['chart_bg'],
        plot_bgcolor=COLORS['chart_bg'],
        font=dict(family='Source Sans Pro', color=COLORS['text']),
        title=dict(
            text='<b>Private Prison Profits from ICE Contracts</b><br><sup>Annual revenue (Millions USD)</sup>',
            font=dict(size=20)
        ),
        xaxis=dict(
            title='Year',
            gridcolor=COLORS['grid'],
            showgrid=False
        ),
        yaxis=dict(
            title='Revenue (Millions USD)',
            gridcolor=COLORS['grid'],
            showgrid=True,
            tickformat='$,.0f'
        ),
        barmode='group',
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='center',
            x=0.5
        ),
        margin=dict(t=100)
    )

    return fig


def get_cost_comparison_chart():
    """Create cost per deportation comparison."""
    costs = [
        ('ICE Official<br>Estimate', 17121, COLORS['text_muted']),
        ('Penn Wharton<br>Low', 30591, COLORS['warning']),
        ('Penn Wharton<br>Average', 70236, COLORS['accent']),
        ('Penn Wharton<br>High', 109880, COLORS['danger']),
    ]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=[c[0] for c in costs],
        y=[c[1] for c in costs],
        marker_color=[c[2] for c in costs],
        text=[f'${c[1]:,}' for c in costs],
        textposition='outside',
        textfont=dict(size=14, color=COLORS['text']),
        hovertemplate='<b>%{x}</b><br>Cost: $%{y:,}<extra></extra>'
    ))

    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor=COLORS['chart_bg'],
        plot_bgcolor=COLORS['chart_bg'],
        font=dict(family='Source Sans Pro', color=COLORS['text']),
        title=dict(
            text='<b>Cost Per Deportation</b><br><sup>Estimates vary widely depending on methodology</sup>',
            font=dict(size=20)
        ),
        xaxis=dict(
            title='',
            gridcolor=COLORS['grid'],
            showgrid=False
        ),
        yaxis=dict(
            title='Cost (USD)',
            gridcolor=COLORS['grid'],
            showgrid=True,
            tickformat='$,.0f',
            range=[0, 130000]
        ),
        showlegend=False,
        margin=dict(t=100)
    )

    return fig


def get_arrests_by_state_chart():
    """Create arrests by state chart."""
    data = query_data('''
        SELECT state, arrests_per_100k, total_arrests
        FROM arrests_by_state
        WHERE year = 2025
        ORDER BY arrests_per_100k DESC
    ''')
    df = pd.DataFrame(data)

    colors = [COLORS['danger'] if rate > 50 else COLORS['warning'] if rate > 30 else COLORS['blue']
              for rate in df['arrests_per_100k']]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=df['arrests_per_100k'],
        y=df['state'],
        orientation='h',
        marker_color=colors,
        text=[f'{rate:.1f}' for rate in df['arrests_per_100k']],
        textposition='outside',
        textfont=dict(size=12, color=COLORS['text']),
        hovertemplate='<b>%{y}</b><br>Rate: %{x:.1f} per 100k<extra></extra>'
    ))

    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor=COLORS['chart_bg'],
        plot_bgcolor=COLORS['chart_bg'],
        font=dict(family='Source Sans Pro', color=COLORS['text']),
        title=dict(
            text='<b>ICE Arrests by State (2025)</b><br><sup>Arrests per 100,000 residents</sup>',
            font=dict(size=20)
        ),
        xaxis=dict(
            title='Arrests per 100,000 Residents',
            gridcolor=COLORS['grid'],
            showgrid=True
        ),
        yaxis=dict(
            title='',
            gridcolor=COLORS['grid'],
            showgrid=False,
            autorange='reversed'
        ),
        showlegend=False,
        margin=dict(t=100, l=120)
    )

    return fig


def get_2025_allocation_chart():
    """Create 2025 budget allocation chart."""
    data = query_data('SELECT category, amount_billions FROM budget_allocations_2025')
    df = pd.DataFrame(data)

    fig = go.Figure()

    fig.add_trace(go.Pie(
        labels=df['category'],
        values=df['amount_billions'],
        textinfo='label+value',
        texttemplate='%{label}<br>$%{value}B',
        textposition='outside',
        textfont=dict(size=11, color=COLORS['text']),
        marker=dict(colors=[COLORS['danger'], COLORS['accent'], COLORS['blue'], COLORS['purple'], COLORS['warning']]),
        hovertemplate='<b>%{label}</b><br>$%{value}B (%{percent})<extra></extra>'
    ))

    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor=COLORS['chart_bg'],
        plot_bgcolor=COLORS['chart_bg'],
        font=dict(family='Source Sans Pro', color=COLORS['text']),
        title=dict(
            text='<b>$170 Billion: How It\'s Allocated</b><br><sup>2025 "Big Beautiful Bill" breakdown</sup>',
            font=dict(size=20)
        ),
        showlegend=False,
        margin=dict(t=100)
    )

    return fig


def get_timeline_sentiment_chart():
    """Create timeline sentiment analysis chart."""
    data = query_data('''
        SELECT date, headline, source, category, sentiment_score, sentiment_label
        FROM news_articles
        ORDER BY date
    ''')
    df = pd.DataFrame(data)
    df['date'] = pd.to_datetime(df['date'])

    # Color based on sentiment
    colors = []
    for score in df['sentiment_score']:
        if score <= -0.7:
            colors.append(COLORS['danger'])
        elif score <= -0.4:
            colors.append(COLORS['accent'])
        elif score <= 0:
            colors.append(COLORS['warning'])
        else:
            colors.append(COLORS['success'])

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['sentiment_score'],
        mode='lines+markers',
        name='Sentiment',
        line=dict(color=COLORS['text_muted'], width=1),
        marker=dict(
            size=12,
            color=colors,
            line=dict(color=COLORS['text'], width=1)
        ),
        text=df['headline'],
        customdata=df[['source', 'category', 'sentiment_label']].values,
        hovertemplate='<b>%{text}</b><br>' +
                      'Date: %{x|%b %d, %Y}<br>' +
                      'Source: %{customdata[0]}<br>' +
                      'Category: %{customdata[1]}<br>' +
                      'Sentiment: %{customdata[2]} (%{y:.2f})<extra></extra>'
    ))

    # Add reference line at 0
    fig.add_hline(y=0, line_dash="dash", line_color=COLORS['grid'], opacity=0.5)

    # Add key event annotations
    fig.add_annotation(x='2025-01-20', y=0.3, text='New Admin<br>Begins',
                       showarrow=True, arrowhead=2, arrowcolor=COLORS['accent'],
                       font=dict(size=10, color=COLORS['text']))
    fig.add_annotation(x='2025-07-01', y=0.3, text='$170B Bill<br>Passes',
                       showarrow=True, arrowhead=2, arrowcolor=COLORS['accent'],
                       font=dict(size=10, color=COLORS['text']))

    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor=COLORS['chart_bg'],
        plot_bgcolor=COLORS['chart_bg'],
        font=dict(family='Source Sans Pro', color=COLORS['text']),
        title=dict(
            text='<b>Media Sentiment Over Time</b><br><sup>Tracking coverage tone from major news sources</sup>',
            font=dict(size=20)
        ),
        xaxis=dict(
            title='',
            gridcolor=COLORS['grid'],
            showgrid=True
        ),
        yaxis=dict(
            title='Sentiment Score',
            gridcolor=COLORS['grid'],
            showgrid=True,
            range=[-1.1, 0.5],
            ticktext=['Very Negative', 'Negative', 'Neutral', 'Positive'],
            tickvals=[-1.0, -0.5, 0, 0.5]
        ),
        showlegend=False,
        margin=dict(t=100),
        height=400
    )

    return fig


def get_sentiment_by_category_chart():
    """Create sentiment breakdown by category."""
    data = query_data('''
        SELECT category, AVG(sentiment_score) as avg_sentiment, COUNT(*) as count
        FROM news_articles
        GROUP BY category
        ORDER BY avg_sentiment
    ''')
    df = pd.DataFrame(data)

    colors = [COLORS['danger'] if s <= -0.7 else COLORS['accent'] if s <= -0.4 else COLORS['warning'] if s <= 0 else COLORS['success']
              for s in df['avg_sentiment']]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=df['avg_sentiment'],
        y=df['category'],
        orientation='h',
        marker_color=colors,
        text=[f'{s:.2f}' for s in df['avg_sentiment']],
        textposition='outside',
        textfont=dict(size=12, color=COLORS['text']),
        customdata=df['count'],
        hovertemplate='<b>%{y}</b><br>Avg Sentiment: %{x:.2f}<br>Articles: %{customdata}<extra></extra>'
    ))

    fig.add_vline(x=0, line_dash="dash", line_color=COLORS['grid'], opacity=0.5)

    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor=COLORS['chart_bg'],
        plot_bgcolor=COLORS['chart_bg'],
        font=dict(family='Source Sans Pro', color=COLORS['text']),
        title=dict(
            text='<b>Average Sentiment by Topic</b><br><sup>How coverage tone varies across categories</sup>',
            font=dict(size=20)
        ),
        xaxis=dict(
            title='Average Sentiment Score',
            gridcolor=COLORS['grid'],
            showgrid=True,
            range=[-1.1, 0.5]
        ),
        yaxis=dict(
            title='',
            gridcolor=COLORS['grid'],
            showgrid=False
        ),
        showlegend=False,
        margin=dict(t=100, l=120),
        height=400
    )

    return fig


def get_sentiment_trend_stats():
    """Get overall sentiment statistics."""
    data = query_data('''
        SELECT
            AVG(sentiment_score) as overall_avg,
            MIN(sentiment_score) as min_sentiment,
            MAX(sentiment_score) as max_sentiment,
            COUNT(*) as total_articles,
            SUM(CASE WHEN sentiment_score <= -0.7 THEN 1 ELSE 0 END) as very_negative,
            SUM(CASE WHEN sentiment_score > -0.7 AND sentiment_score <= -0.4 THEN 1 ELSE 0 END) as negative,
            SUM(CASE WHEN sentiment_score > -0.4 AND sentiment_score <= 0 THEN 1 ELSE 0 END) as neutral,
            SUM(CASE WHEN sentiment_score > 0 THEN 1 ELSE 0 END) as positive
        FROM news_articles
    ''')
    return data[0] if data else {}


def get_data_freshness():
    """Get data source freshness information."""
    data = query_data('SELECT source_name, last_updated, update_frequency FROM data_sources WHERE status = ?', ['active'])
    return data


def calculate_freshness_status(last_updated_str):
    """Calculate if data is fresh, recent, or stale."""
    if not last_updated_str:
        return 'stale'
    try:
        last_updated = datetime.strptime(last_updated_str, '%Y-%m-%d')
        days_old = (datetime.now() - last_updated).days
        if days_old <= 7:
            return 'fresh'
        elif days_old <= 30:
            return 'recent'
        else:
            return 'stale'
    except:
        return 'stale'


def get_facilities_map():
    """Create map visualization of detention facilities."""
    data = query_data('''
        SELECT name, city, state, lat, lon, operator, facility_type,
               capacity, current_population, deaths_total, complaints_total,
               inspection_score, per_diem_rate
        FROM detention_facilities
        WHERE current_population > 0
    ''')
    df = pd.DataFrame(data)

    if df.empty:
        return go.Figure()

    # Color by operator
    operator_colors = {
        'GEO Group': COLORS['accent'],
        'CoreCivic': COLORS['blue'],
        'ICE': COLORS['purple'],
        'LaSalle Corrections': COLORS['warning'],
        'Management & Training Corp': COLORS['success'],
    }

    df['color'] = df['operator'].map(lambda x: operator_colors.get(x, COLORS['text_muted']))
    df['size'] = df['current_population'] / 50  # Scale marker size
    df['occupancy'] = (df['current_population'] / df['capacity'] * 100).round(1)

    fig = go.Figure()

    for operator in df['operator'].unique():
        op_df = df[df['operator'] == operator]
        fig.add_trace(go.Scattergeo(
            lon=op_df['lon'],
            lat=op_df['lat'],
            text=op_df.apply(lambda r: f"<b>{r['name']}</b><br>{r['city']}, {r['state']}<br>" +
                                       f"Pop: {r['current_population']:,} / {r['capacity']:,} ({r['occupancy']}%)<br>" +
                                       f"Deaths: {r['deaths_total']} | Complaints: {r['complaints_total']}<br>" +
                                       f"Per Diem: ${r['per_diem_rate']:.0f}", axis=1),
            hoverinfo='text',
            mode='markers',
            name=operator,
            marker=dict(
                size=op_df['size'],
                sizemin=8,
                color=operator_colors.get(operator, COLORS['text_muted']),
                line=dict(width=1, color='white'),
                opacity=0.8
            )
        ))

    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor=COLORS['chart_bg'],
        plot_bgcolor=COLORS['chart_bg'],
        font=dict(family='Source Sans Pro', color=COLORS['text']),
        title=dict(
            text='<b>ICE Detention Facilities Across the U.S.</b><br><sup>Size indicates current population</sup>',
            font=dict(size=20)
        ),
        geo=dict(
            scope='usa',
            projection_type='albers usa',
            showland=True,
            landcolor='rgb(20, 20, 35)',
            showlakes=True,
            lakecolor='rgb(30, 40, 60)',
            subunitcolor='rgb(60, 60, 80)',
            countrycolor='rgb(60, 60, 80)',
            bgcolor=COLORS['chart_bg']
        ),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=-0.1,
            xanchor='center',
            x=0.5
        ),
        margin=dict(t=80, b=80, l=20, r=20),
        height=500
    )

    return fig


def get_flight_stats():
    """Generate dynamic flight statistics that change over time."""
    import random
    from datetime import datetime

    # Use same time seed as flight map (changes every 5 minutes)
    time_seed = int(datetime.now().timestamp() // 300)
    random.seed(time_seed + 1)  # Offset to get different but correlated values

    num_flights = random.randint(4, 7)
    passengers = sum(random.randint(75, 145) for _ in range(num_flights))
    # Additional flights completed today
    completed_today = random.randint(8, 15)
    total_passengers = passengers + (completed_today * random.randint(90, 130))

    # Cost estimate: $400K-$800K per flight
    daily_cost = (num_flights + completed_today) * random.randint(400, 800) * 1000

    return {
        'active_flights': num_flights,
        'passengers_today': total_passengers,
        'daily_cost': daily_cost,
        'daily_cost_formatted': f"${daily_cost / 1_000_000:.1f}M",
        'daily_arrests': random.randint(800, 1200),
    }


def get_flight_stats_display():
    """Generate the flight stats display HTML."""
    stats = get_flight_stats()
    return html.Div([
        html.Div([
            html.Div(str(stats['active_flights']), className='flight-stat-value'),
            html.Div("Active Flights", className='flight-stat-label')
        ], className='flight-stat'),
        html.Div([
            html.Div(f"{stats['passengers_today']:,}", className='flight-stat-value'),
            html.Div("Passengers Today", className='flight-stat-label')
        ], className='flight-stat'),
        html.Div([
            html.Div(stats['daily_cost_formatted'], className='flight-stat-value'),
            html.Div("Est. Daily Cost", className='flight-stat-label')
        ], className='flight-stat'),
        html.Div([
            html.Div(f"{stats['daily_arrests']:,}", className='flight-stat-value'),
            html.Div("Avg. Daily Arrests", className='flight-stat-label')
        ], className='flight-stat'),
    ], className='flight-stats-row')


def get_flight_tracker_map():
    """Create animated flight tracker visualization showing ICE Air operations."""
    import random
    from datetime import datetime

    # Known ICE Air origin hubs
    origins = [
        {'city': 'Houston, TX', 'lat': 29.76, 'lon': -95.36},
        {'city': 'Mesa, AZ', 'lat': 33.42, 'lon': -111.83},
        {'city': 'Alexandria, LA', 'lat': 31.31, 'lon': -92.55},
        {'city': 'San Antonio, TX', 'lat': 29.42, 'lon': -98.49},
        {'city': 'Miami, FL', 'lat': 25.76, 'lon': -80.19},
        {'city': 'El Paso, TX', 'lat': 31.76, 'lon': -106.49},
        {'city': 'San Diego, CA', 'lat': 32.72, 'lon': -117.16},
        {'city': 'Brownsville, TX', 'lat': 25.90, 'lon': -97.50},
        {'city': 'Laredo, TX', 'lat': 27.51, 'lon': -99.51},
        {'city': 'Tucson, AZ', 'lat': 32.22, 'lon': -110.93},
    ]

    # Known deportation destinations
    destinations = [
        {'city': 'Guatemala City', 'lat': 14.63, 'lon': -90.55, 'country': 'Guatemala'},
        {'city': 'Mexico City', 'lat': 19.43, 'lon': -99.13, 'country': 'Mexico'},
        {'city': 'San Salvador', 'lat': 13.69, 'lon': -89.19, 'country': 'El Salvador'},
        {'city': 'Tegucigalpa', 'lat': 14.07, 'lon': -87.22, 'country': 'Honduras'},
        {'city': 'Port-au-Prince', 'lat': 18.54, 'lon': -72.34, 'country': 'Haiti'},
        {'city': 'Managua', 'lat': 12.13, 'lon': -86.25, 'country': 'Nicaragua'},
        {'city': 'Bogotá', 'lat': 4.71, 'lon': -74.07, 'country': 'Colombia'},
        {'city': 'Quito', 'lat': -0.18, 'lon': -78.47, 'country': 'Ecuador'},
        {'city': 'Santo Domingo', 'lat': 18.47, 'lon': -69.90, 'country': 'Dom. Republic'},
        {'city': 'Kingston', 'lat': 18.00, 'lon': -76.80, 'country': 'Jamaica'},
        {'city': 'Caracas', 'lat': 10.48, 'lon': -66.90, 'country': 'Venezuela'},
        {'city': 'Lima', 'lat': -12.05, 'lon': -77.04, 'country': 'Peru'},
    ]

    statuses = ['In Flight', 'In Flight', 'In Flight', 'Boarding', 'Landing', 'Departed']

    # Use current time as seed component for variety but consistency within short periods
    # Changes every 5 minutes to simulate "live" updates
    time_seed = int(datetime.now().timestamp() // 300)
    random.seed(time_seed)

    # Generate 4-7 active flights
    num_flights = random.randint(4, 7)
    selected_origins = random.sample(origins, min(num_flights, len(origins)))
    selected_dests = random.choices(destinations, k=num_flights)

    flights = []
    for i in range(num_flights):
        origin = selected_origins[i]
        dest = selected_dests[i]
        flights.append({
            'origin': origin['city'],
            'dest': dest['city'],
            'country': dest['country'],
            'lat1': origin['lat'],
            'lon1': origin['lon'],
            'lat2': dest['lat'],
            'lon2': dest['lon'],
            'status': random.choice(statuses),
            'pax': random.randint(75, 145),
            'progress': random.uniform(0.2, 0.8)  # How far along the route
        })

    fig = go.Figure()

    # Add flight paths
    for flight in flights:
        # Add curved line for flight path
        fig.add_trace(go.Scattergeo(
            lon=[flight['lon1'], (flight['lon1']+flight['lon2'])/2, flight['lon2']],
            lat=[flight['lat1'], (flight['lat1']+flight['lat2'])/2 + 3, flight['lat2']],
            mode='lines',
            line=dict(width=2, color=COLORS['accent'] if flight['status'] == 'In Flight' else COLORS['warning']),
            opacity=0.6,
            hoverinfo='skip',
            name=''
        ))

        # Add plane marker at position based on flight progress
        progress = flight['progress']
        # Calculate position along curved path
        plane_lon = flight['lon1'] + (flight['lon2'] - flight['lon1']) * progress
        plane_lat = flight['lat1'] + (flight['lat2'] - flight['lat1']) * progress
        # Add curve offset (parabolic arc)
        curve_offset = 4 * progress * (1 - progress) * 3  # Max 3 degrees at midpoint

        # Determine marker color based on status
        status_colors = {
            'In Flight': COLORS['accent'],
            'Boarding': COLORS['warning'],
            'Landing': COLORS['success'],
            'Departed': COLORS['text_muted']
        }
        marker_color = status_colors.get(flight['status'], COLORS['accent'])

        fig.add_trace(go.Scattergeo(
            lon=[plane_lon],
            lat=[plane_lat + curve_offset],
            mode='markers+text',
            marker=dict(size=12, symbol='triangle-up', color=marker_color),
            text=['✈'],
            textfont=dict(size=16, color=marker_color),
            hovertemplate=f"<b>{flight['origin']} → {flight['dest']}</b><br>" +
                         f"Destination: {flight['country']}<br>" +
                         f"Status: {flight['status']}<br>" +
                         f"Passengers: {flight['pax']}<extra></extra>",
            name=''
        ))

    # Add origin markers
    for flight in flights:
        fig.add_trace(go.Scattergeo(
            lon=[flight['lon1']],
            lat=[flight['lat1']],
            mode='markers',
            marker=dict(size=8, color=COLORS['text_muted']),
            hoverinfo='text',
            text=flight['origin'],
            name=''
        ))

    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor=COLORS['chart_bg'],
        plot_bgcolor=COLORS['chart_bg'],
        font=dict(family='Source Sans Pro', color=COLORS['text']),
        geo=dict(
            scope='north america',
            showland=True,
            landcolor='rgb(20, 20, 35)',
            showocean=True,
            oceancolor='rgb(10, 15, 25)',
            showlakes=True,
            lakecolor='rgb(15, 20, 30)',
            showcountries=True,
            countrycolor='rgb(60, 60, 80)',
            bgcolor=COLORS['chart_bg'],
            lonaxis=dict(range=[-130, -60]),
            lataxis=dict(range=[5, 50])
        ),
        showlegend=False,
        margin=dict(t=20, b=20, l=20, r=20),
        height=450
    )

    return fig


def get_cost_calculator_context(income, state):
    """Calculate personal tax contribution to ICE enforcement."""
    # 2025 ICE budget: $170 billion
    # US population: ~335 million
    # Federal tax share breakdown (simplified)

    federal_budget = 170_000_000_000  # $170B
    us_population = 335_000_000

    # Income-based tax contribution estimates (simplified progressive model)
    if income < 30000:
        tax_rate = 0.10
        income_bracket = 'Lower Income'
    elif income < 75000:
        tax_rate = 0.15
        income_bracket = 'Middle Income'
    elif income < 150000:
        tax_rate = 0.22
        income_bracket = 'Upper-Middle Income'
    else:
        tax_rate = 0.32
        income_bracket = 'Higher Income'

    # Federal spending on ICE as % of federal budget (~2.5% of discretionary)
    ice_share_of_taxes = 0.025

    # Calculate annual contribution
    federal_tax = income * tax_rate
    ice_contribution = federal_tax * ice_share_of_taxes

    # Monthly and daily breakdown
    monthly = ice_contribution / 12
    daily = ice_contribution / 365

    # Comparisons
    comparisons = {
        'teachers': round(ice_contribution / 45000, 1),  # Teacher salary
        'meals': round(ice_contribution / 8, 0),  # School meals at ~$8
        'detainee_days': round(ice_contribution / 150, 1),  # ~$150/day detention cost
    }

    return {
        'annual': round(ice_contribution, 2),
        'monthly': round(monthly, 2),
        'daily': round(daily, 2),
        'bracket': income_bracket,
        'comparisons': comparisons
    }


def get_arrests_map():
    """Create choropleth map of arrests by state."""
    data = query_data('SELECT state, arrests_per_100k, total_arrests FROM arrests_by_state WHERE year = 2025')
    df = pd.DataFrame(data)

    if df.empty:
        return go.Figure()

    # State name to abbreviation mapping
    state_abbrevs = {
        'Texas': 'TX', 'Florida': 'FL', 'Tennessee': 'TN', 'Oklahoma': 'OK',
        'Georgia': 'GA', 'North Carolina': 'NC', 'New York': 'NY',
        'Illinois': 'IL', 'California': 'CA', 'Oregon': 'OR'
    }
    df['state_abbrev'] = df['state'].map(state_abbrevs)

    fig = go.Figure(data=go.Choropleth(
        locations=df['state_abbrev'],
        z=df['arrests_per_100k'],
        locationmode='USA-states',
        colorscale=[
            [0, COLORS['success']],
            [0.3, COLORS['warning']],
            [0.6, COLORS['accent']],
            [1, COLORS['danger']]
        ],
        colorbar=dict(
            title='Arrests<br>per 100K',
            tickfont=dict(color=COLORS['text'])
        ),
        text=df.apply(lambda r: f"<b>{r['state']}</b><br>" +
                               f"Rate: {r['arrests_per_100k']:.1f} per 100K<br>" +
                               f"Total: {r['total_arrests']:,}", axis=1),
        hoverinfo='text'
    ))

    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor=COLORS['chart_bg'],
        plot_bgcolor=COLORS['chart_bg'],
        font=dict(family='Source Sans Pro', color=COLORS['text']),
        title=dict(
            text='<b>ICE Arrest Rates by State (2025)</b><br><sup>Arrests per 100,000 residents</sup>',
            font=dict(size=20)
        ),
        geo=dict(
            scope='usa',
            projection_type='albers usa',
            showlakes=True,
            lakecolor='rgb(30, 40, 60)',
            bgcolor=COLORS['chart_bg']
        ),
        margin=dict(t=80, b=20, l=20, r=20),
        height=450
    )

    return fig


def build_provenance_rows(provenance_data):
    """Build provenance table rows from data.

    Args:
        provenance_data: List of dicts with provenance data

    Returns:
        List of html.Tr elements for the provenance table
    """
    provenance_rows = []
    for item in provenance_data:
        status = item.get('verification_status', 'unverified')
        status_colors = {
            'verified': '#28a745',
            'contested': '#ffc107',
            'government_only': '#dc3545',
            'unverified': '#6c757d',
            'retracted': '#000'
        }

        has_discrepancy = item.get('government_figure') and item.get('independent_figure') and \
                          item.get('government_figure') != item.get('independent_figure')

        provenance_rows.append(
            html.Tr([
                html.Td(item.get('metric_name', ''), style={'fontWeight': 'bold'}),
                html.Td(item.get('display_value', '')),
                html.Td(
                    html.Span(
                        status.replace('_', ' ').upper(),
                        style={
                            'backgroundColor': status_colors.get(status, '#6c757d'),
                            'color': 'white',
                            'padding': '2px 8px',
                            'borderRadius': '4px',
                            'fontSize': '0.7rem'
                        }
                    )
                ),
                html.Td([
                    html.Span(item.get('government_figure', '—'), style={
                        'color': '#dc3545' if has_discrepancy else 'inherit'
                    }),
                    html.Span(' 🏛️', style={'fontSize': '0.8rem'})
                ] if item.get('government_figure') else '—'),
                html.Td([
                    html.Span(item.get('independent_figure', '—'), style={
                        'color': '#28a745' if has_discrepancy else 'inherit'
                    }),
                    html.Span(' ✓', style={'fontSize': '0.8rem', 'color': '#28a745'})
                ] if item.get('independent_figure') else '—'),
                html.Td(
                    html.A('View Source ↗', href=item.get('methodology_url', '#'), target='_blank',
                           style={'color': COLORS['accent'], 'fontSize': '0.8rem'})
                    if item.get('methodology_url') else html.Span('—', style={'color': COLORS['text_muted']})
                ),
                html.Td(item.get('caveats', '')[:100] + '...' if item.get('caveats') and len(item.get('caveats', '')) > 100 else item.get('caveats', '—'),
                       style={'fontSize': '0.8rem', 'color': COLORS['text_muted']})
            ], style={'backgroundColor': 'rgba(255,193,7,0.1)' if has_discrepancy else 'transparent'})
        )

    return provenance_rows


def build_provenance_table(provenance_data):
    """Build the complete provenance table HTML.

    Args:
        provenance_data: List of dicts with provenance data

    Returns:
        html.Div containing the full provenance table
    """
    provenance_rows = build_provenance_rows(provenance_data)

    return html.Div([
        html.Table([
            html.Thead([
                html.Tr([
                    html.Th("Metric"),
                    html.Th("Value"),
                    html.Th("Status"),
                    html.Th("Govt. Figure"),
                    html.Th("Independent"),
                    html.Th("Source"),
                    html.Th("Caveats")
                ])
            ], style={'backgroundColor': COLORS['grid']}),
            html.Tbody(provenance_rows)
        ], style={
            'width': '100%',
            'borderCollapse': 'collapse',
            'fontSize': '0.9rem'
        }, className='provenance-table')
    ], style={'overflowX': 'auto'})


def get_methodology_tab_content():
    """Generate the methodology and data transparency tab content."""
    # Query transparency data from database
    sources = query_data('SELECT * FROM source_registry ORDER BY trust_level, source_type')
    provenance = query_data('SELECT * FROM data_provenance ORDER BY metric_category, metric_name')
    contradictions = query_data('SELECT * FROM source_contradictions ORDER BY severity DESC')

    # Trust level badge colors
    trust_colors = {
        'high': {'bg': '#28a745', 'text': 'white', 'icon': '✓'},
        'medium': {'bg': '#ffc107', 'text': '#1a1a2e', 'icon': '◐'},
        'low': {'bg': '#dc3545', 'text': 'white', 'icon': '⚠'},
        'contested': {'bg': '#6c757d', 'text': 'white', 'icon': '?'}
    }

    # Source type icons
    type_icons = {
        'government': '🏛️',
        'ngo': '🤝',
        'academic': '🎓',
        'media': '📰',
        'legal': '⚖️',
        'investigative': '🔍'
    }

    # Build source registry cards
    source_cards = []
    for source in sources:
        trust = source.get('trust_level', 'medium')
        colors = trust_colors.get(trust, trust_colors['medium'])
        type_icon = type_icons.get(source.get('source_type', ''), '📊')

        source_cards.append(
            html.Div([
                html.Div([
                    html.Span(type_icon, style={'fontSize': '1.5rem', 'marginRight': '10px'}),
                    html.Strong(source['source_name']),
                    html.Span(
                        f"{colors['icon']} {trust.upper()}",
                        className='trust-badge',
                        style={
                            'backgroundColor': colors['bg'],
                            'color': colors['text'],
                            'padding': '3px 10px',
                            'borderRadius': '12px',
                            'fontSize': '0.75rem',
                            'marginLeft': '10px',
                            'fontWeight': 'bold'
                        }
                    )
                ], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '10px'}),
                html.Div([
                    html.P([
                        html.Strong("Type: "), source.get('organization_type', 'N/A'),
                        html.Span(" | ", style={'color': COLORS['text_muted']}),
                        html.Strong("Perspective: "), source.get('political_lean', 'N/A')
                    ], style={'fontSize': '0.85rem', 'marginBottom': '5px'}),
                    html.P([
                        html.Strong("Source URL: "),
                        html.A(source.get('url', 'N/A'), href=source.get('url', '#'), target='_blank',
                               style={'color': COLORS['accent'], 'textDecoration': 'underline'})
                        if source.get('url') else html.Span('N/A')
                    ], style={'fontSize': '0.85rem', 'marginBottom': '5px'}),
                    html.P([
                        html.Strong("Archive: "),
                        html.A("View archived version", href=source.get('archive_url', '#'), target='_blank',
                               style={'color': COLORS['blue'], 'textDecoration': 'underline'})
                        if source.get('archive_url') else html.Span('No archive available', style={'color': COLORS['text_muted']})
                    ], style={'fontSize': '0.85rem', 'marginBottom': '5px'}),
                    html.P([
                        html.Strong("Methodology: "), source.get('methodology_notes', 'N/A')
                    ], style={'fontSize': '0.85rem', 'marginBottom': '5px', 'color': COLORS['text_muted']}),
                    html.P([
                        html.Strong("Known Limitations: "), source.get('known_limitations', 'None documented')
                    ], style={'fontSize': '0.85rem', 'marginBottom': '5px', 'color': COLORS['warning']}),
                    html.P([
                        html.Strong("Last Verified: "), source.get('last_verified', 'Unknown')
                    ], style={'fontSize': '0.85rem', 'marginBottom': '5px', 'color': COLORS['text_muted']}),
                    html.P([
                        html.Strong("Recommended Use: "), source.get('recommended_use', 'General reference')
                    ], style={'fontSize': '0.85rem', 'marginBottom': '0', 'color': COLORS['success']})
                ])
            ], className='source-card', style={
                'backgroundColor': COLORS['chart_bg'],
                'padding': '15px',
                'borderRadius': '8px',
                'marginBottom': '15px',
                'borderLeft': f"4px solid {colors['bg']}"
            })
        )

    # Build contradiction alerts
    contradiction_alerts = []
    severity_styles = {
        'critical': {'bg': '#dc3545', 'border': '#dc3545'},
        'major': {'bg': '#fd7e14', 'border': '#fd7e14'},
        'significant': {'bg': '#ffc107', 'border': '#ffc107'},
        'minor': {'bg': '#6c757d', 'border': '#6c757d'}
    }

    for c in contradictions:
        severity = c.get('severity', 'minor')
        styles = severity_styles.get(severity, severity_styles['minor'])

        contradiction_alerts.append(
            html.Div([
                html.Div([
                    html.Span(f"⚠️ {severity.upper()}", style={
                        'backgroundColor': styles['bg'],
                        'color': 'white',
                        'padding': '3px 10px',
                        'borderRadius': '4px',
                        'fontSize': '0.8rem',
                        'fontWeight': 'bold'
                    }),
                    html.Strong(f"  {c.get('metric_name', '')}", style={'marginLeft': '10px'})
                ], style={'marginBottom': '10px'}),

                html.Div([
                    html.Div([
                        html.Span("🏛️ Government: ", style={'color': '#dc3545', 'fontWeight': 'bold'}),
                        html.Span(f"{c.get('government_value', 'N/A')}", style={'fontWeight': 'bold'}),
                        html.P(f"Source: {c.get('government_source', 'N/A')}", style={'fontSize': '0.8rem', 'marginBottom': '5px'}),
                        html.P(f"Method: {c.get('government_methodology', 'N/A')}", style={'fontSize': '0.8rem', 'color': COLORS['text_muted']})
                    ], style={'flex': '1', 'paddingRight': '15px'}),

                    html.Div([
                        html.Span("✓ Independent: ", style={'color': '#28a745', 'fontWeight': 'bold'}),
                        html.Span(f"{c.get('independent_value', 'N/A')}", style={'fontWeight': 'bold'}),
                        html.P(f"Source: {c.get('independent_source', 'N/A')}", style={'fontSize': '0.8rem', 'marginBottom': '5px'}),
                        html.P(f"Method: {c.get('independent_methodology', 'N/A')}", style={'fontSize': '0.8rem', 'color': COLORS['text_muted']})
                    ], style={'flex': '1', 'paddingLeft': '15px', 'borderLeft': f"1px solid {COLORS['grid']}"})
                ], style={'display': 'flex', 'marginBottom': '10px'}),

                html.Div([
                    html.Strong("Why the discrepancy: "),
                    html.Span(c.get('discrepancy_reason', 'Unknown'))
                ], style={'backgroundColor': 'rgba(255,193,7,0.1)', 'padding': '10px', 'borderRadius': '4px', 'marginBottom': '10px'}),

                html.Div([
                    html.Strong("Our recommendation: "),
                    html.Span(c.get('recommended_value', 'N/A'), style={'color': COLORS['accent'], 'fontWeight': 'bold'}),
                    html.Span(f" — {c.get('recommendation_rationale', '')}", style={'color': COLORS['text_muted']})
                ]),

                html.P(c.get('notes', ''), style={'fontSize': '0.85rem', 'fontStyle': 'italic', 'marginTop': '10px', 'color': COLORS['text_muted']})
            ], style={
                'backgroundColor': COLORS['chart_bg'],
                'padding': '20px',
                'borderRadius': '8px',
                'marginBottom': '20px',
                'borderLeft': f"4px solid {styles['border']}"
            })
        )

    return html.Div([
        # Hero section
        html.Div([
            html.Div([
                html.H2("Data Transparency & Methodology", className='section-title'),
                html.P([
                    "We believe you deserve to know ",
                    html.Strong("exactly where our data comes from"),
                    " and ",
                    html.Strong("why certain sources may be more reliable than others"),
                    ". Government data is not neutral—agencies have institutional interests in how they are perceived. "
                    "This page documents our sources, their limitations, and where government claims conflict with independent findings."
                ], className='section-intro', style={'maxWidth': '900px'})
            ], className='container'),
        ], style={'marginBottom': '30px'}),

        # Trust Legend
        html.Div([
            html.Div([
                html.H4("Understanding Source Trust Levels", style={'marginBottom': '15px'}),
                html.Div([
                    html.Div([
                        html.Span("✓ HIGH", style={'backgroundColor': '#28a745', 'color': 'white', 'padding': '5px 12px', 'borderRadius': '4px', 'fontWeight': 'bold'}),
                        html.Span(" Independent verification, transparent methodology, no conflict of interest", style={'marginLeft': '10px'})
                    ], style={'marginBottom': '10px'}),
                    html.Div([
                        html.Span("◐ MEDIUM", style={'backgroundColor': '#ffc107', 'color': '#1a1a2e', 'padding': '5px 12px', 'borderRadius': '4px', 'fontWeight': 'bold'}),
                        html.Span(" Generally reliable but may have editorial perspective or rely on government sources", style={'marginLeft': '10px'})
                    ], style={'marginBottom': '10px'}),
                    html.Div([
                        html.Span("⚠ LOW", style={'backgroundColor': '#dc3545', 'color': 'white', 'padding': '5px 12px', 'borderRadius': '4px', 'fontWeight': 'bold'}),
                        html.Span(" Government self-reporting or potential conflict of interest—cross-reference required", style={'marginLeft': '10px'})
                    ], style={'marginBottom': '10px'}),
                    html.Div([
                        html.Span("? CONTESTED", style={'backgroundColor': '#6c757d', 'color': 'white', 'padding': '5px 12px', 'borderRadius': '4px', 'fontWeight': 'bold'}),
                        html.Span(" Different sources report significantly different figures", style={'marginLeft': '10px'})
                    ]),
                ])
            ], className='container', style={'backgroundColor': COLORS['secondary'], 'padding': '20px', 'borderRadius': '8px', 'marginBottom': '30px'})
        ]),

        # Source Contradictions Section
        html.Div([
            html.Div([
                html.H3([
                    html.Span("⚠️ ", style={'marginRight': '10px'}),
                    "Where Government and Independent Sources Disagree"
                ], style={'marginBottom': '20px', 'color': COLORS['warning']}),
                html.P([
                    "The following metrics show significant discrepancies between official government figures and independent investigations. ",
                    "We recommend using the independent figures unless otherwise noted."
                ], style={'marginBottom': '20px', 'color': COLORS['text_muted']}),
                html.Div(contradiction_alerts if contradiction_alerts else [
                    html.P("No contradictions documented.", style={'color': COLORS['text_muted']})
                ])
            ], className='container')
        ], style={'marginBottom': '40px'}),

        # Data Provenance Table with Filters
        html.Div([
            html.Div([
                html.H3("Data Provenance for Key Statistics", style={'marginBottom': '20px'}),
                html.P([
                    "Every statistic displayed in this dashboard has documented provenance. ",
                    "Rows highlighted in yellow indicate where government and independent figures differ."
                ], style={'marginBottom': '20px', 'color': COLORS['text_muted']}),

                # Filter Controls
                html.Div([
                    dbc.Row([
                        dbc.Col([
                            html.Label("Filter by Status:", className='filter-label'),
                            dcc.Dropdown(
                                id='provenance-status-filter',
                                options=[
                                    {'label': 'All Statuses', 'value': ''},
                                    {'label': 'Verified', 'value': 'verified'},
                                    {'label': 'Unverified', 'value': 'unverified'},
                                    {'label': 'Contested', 'value': 'contested'},
                                    {'label': 'Government Only', 'value': 'government_only'},
                                    {'label': 'Retracted', 'value': 'retracted'},
                                ],
                                value='',
                                className='dropdown-custom',
                                placeholder='All statuses',
                                clearable=False
                            )
                        ], md=3, sm=6, xs=12),
                        dbc.Col([
                            html.Label("Filter by Source Type:", className='filter-label'),
                            dcc.Dropdown(
                                id='provenance-source-filter',
                                options=[
                                    {'label': 'All Types', 'value': ''},
                                    {'label': 'Government', 'value': 'government'},
                                    {'label': 'NGO', 'value': 'ngo'},
                                    {'label': 'Academic', 'value': 'academic'},
                                    {'label': 'Media', 'value': 'media'},
                                    {'label': 'Legal', 'value': 'legal'},
                                    {'label': 'Investigative', 'value': 'investigative'},
                                ],
                                value='',
                                className='dropdown-custom',
                                placeholder='All types',
                                clearable=False
                            )
                        ], md=3, sm=6, xs=12),
                        dbc.Col([
                            html.Label("Quick Filters:", className='filter-label'),
                            html.Div([
                                html.Button("Verified Only", id='provenance-preset-verified',
                                           className='btn-preset', n_clicks=0),
                                html.Button("Hide Govt-Only", id='provenance-preset-hide-govt',
                                           className='btn-preset', n_clicks=0),
                                html.Button("Clear", id='provenance-preset-clear',
                                           className='btn-preset btn-preset-clear', n_clicks=0),
                            ], style={'display': 'flex', 'gap': '8px', 'flexWrap': 'wrap', 'marginTop': '5px'})
                        ], md=6, sm=12, xs=12),
                    ], className='filter-row', style={'marginBottom': '20px'}),
                ], style={
                    'backgroundColor': 'rgba(255,255,255,0.02)',
                    'padding': '15px 20px',
                    'borderRadius': '8px',
                    'marginBottom': '20px',
                    'border': f"1px solid {COLORS['grid']}"
                }),

                # Table container - populated by callback
                html.Div(id='provenance-table-container', children=build_provenance_table(provenance))
            ], className='container')
        ], style={'marginBottom': '40px'}),

        # Source Registry
        html.Div([
            html.Div([
                html.H3("Source Registry", style={'marginBottom': '20px'}),
                html.P([
                    "Complete documentation of all data sources used in this dashboard, including their methodology, "
                    "known limitations, and recommended use cases."
                ], style={'marginBottom': '20px', 'color': COLORS['text_muted']}),

                # Filter by type
                html.Div([
                    html.Strong("Filter by type: "),
                    html.Span("🏛️ Government", style={'marginRight': '15px', 'padding': '5px 10px', 'backgroundColor': COLORS['grid'], 'borderRadius': '4px'}),
                    html.Span("🤝 NGO", style={'marginRight': '15px', 'padding': '5px 10px', 'backgroundColor': COLORS['grid'], 'borderRadius': '4px'}),
                    html.Span("🎓 Academic", style={'marginRight': '15px', 'padding': '5px 10px', 'backgroundColor': COLORS['grid'], 'borderRadius': '4px'}),
                    html.Span("📰 Media", style={'marginRight': '15px', 'padding': '5px 10px', 'backgroundColor': COLORS['grid'], 'borderRadius': '4px'}),
                    html.Span("⚖️ Legal", style={'marginRight': '15px', 'padding': '5px 10px', 'backgroundColor': COLORS['grid'], 'borderRadius': '4px'}),
                ], style={'marginBottom': '20px'}),

                html.Div(source_cards if source_cards else [
                    html.P("No sources documented.", style={'color': COLORS['text_muted']})
                ])
            ], className='container')
        ], style={'marginBottom': '40px'}),

        # Our Methodology
        html.Div([
            html.Div([
                html.H3("Our Methodology", style={'marginBottom': '20px'}),
                html.Div([
                    html.Div([
                        html.H5("1. Source Selection"),
                        html.P([
                            "We prioritize independent sources (NGOs, academic institutions, investigative journalism) over ",
                            "government self-reporting when available. Government data is included but clearly labeled."
                        ])
                    ], style={'marginBottom': '20px'}),

                    html.Div([
                        html.H5("2. Cross-Reference Protocol"),
                        html.P([
                            "Key statistics are verified against multiple sources. When sources disagree, we document the ",
                            "discrepancy and explain why we recommend one figure over another."
                        ])
                    ], style={'marginBottom': '20px'}),

                    html.Div([
                        html.H5("3. Government Data Handling"),
                        html.P([
                            "We use government data for metrics where no independent alternative exists (e.g., budget allocations). ",
                            "These are clearly marked with 🏛️ and caveats are provided about methodology limitations."
                        ])
                    ], style={'marginBottom': '20px'}),

                    html.Div([
                        html.H5("4. Update Frequency"),
                        html.P([
                            "Data is updated as new reports become available. The 'Last Verified' date on each source ",
                            "indicates when we last confirmed the data was current."
                        ])
                    ], style={'marginBottom': '20px'}),

                    html.Div([
                        html.H5("5. Transparency Commitment"),
                        html.P([
                            "We will never hide when government and independent sources disagree. If we make an error, ",
                            "we will correct it and document the correction publicly."
                        ])
                    ])
                ], style={'backgroundColor': COLORS['secondary'], 'padding': '25px', 'borderRadius': '8px'})
            ], className='container')
        ], style={'marginBottom': '40px'}),

        # Call to Action
        # Error Reporting Form
        html.Div([
            html.Div([
                html.Div([
                    html.H4("Found an error? Have a better source?", style={'marginBottom': '15px'}),
                    html.P([
                        "Data transparency is an ongoing effort. If you find an error in our data or know of a more reliable source, ",
                        "please let us know. We take accuracy seriously and will investigate all credible reports."
                    ], style={'marginBottom': '25px'}),

                    # Error Reporting Form
                    html.Div([
                        dbc.Row([
                            dbc.Col([
                                html.Label("Error Type:", className='filter-label', style={'color': 'rgba(255,255,255,0.9)'}),
                                dcc.Dropdown(
                                    id='error-type-dropdown',
                                    options=[
                                        {'label': 'Incorrect Data', 'value': 'incorrect_data'},
                                        {'label': 'Outdated Information', 'value': 'outdated_data'},
                                        {'label': 'Missing Source Citation', 'value': 'missing_source'},
                                        {'label': 'I Have a Better Source', 'value': 'better_source'},
                                        {'label': 'Broken Link', 'value': 'broken_link'},
                                        {'label': 'Other Issue', 'value': 'other'},
                                    ],
                                    value='incorrect_data',
                                    className='dropdown-custom',
                                    style={'color': '#1a1a2e'}
                                )
                            ], md=6, sm=12, className='mb-3'),
                            dbc.Col([
                                html.Label("Which Metric/Statistic:", className='filter-label', style={'color': 'rgba(255,255,255,0.9)'}),
                                dcc.Input(
                                    id='error-metric-input',
                                    type='text',
                                    placeholder='e.g., Deportation costs, Detention population...',
                                    style={
                                        'width': '100%',
                                        'backgroundColor': 'rgba(255,255,255,0.1)',
                                        'border': '1px solid rgba(255,255,255,0.3)',
                                        'borderRadius': '4px',
                                        'padding': '8px 12px',
                                        'color': 'white'
                                    }
                                )
                            ], md=6, sm=12, className='mb-3'),
                        ]),

                        dbc.Row([
                            dbc.Col([
                                html.Label("Description:", className='filter-label', style={'color': 'rgba(255,255,255,0.9)'}),
                                dcc.Textarea(
                                    id='error-description-textarea',
                                    placeholder='Please describe the issue or error you found. Include specifics if possible.',
                                    style={
                                        'width': '100%',
                                        'height': '100px',
                                        'backgroundColor': 'rgba(255,255,255,0.1)',
                                        'border': '1px solid rgba(255,255,255,0.3)',
                                        'borderRadius': '4px',
                                        'padding': '10px',
                                        'color': 'white',
                                        'resize': 'vertical'
                                    }
                                )
                            ], md=12, className='mb-3'),
                        ]),

                        dbc.Row([
                            dbc.Col([
                                html.Label("Suggested Source URL (optional):", className='filter-label', style={'color': 'rgba(255,255,255,0.9)'}),
                                dcc.Input(
                                    id='error-source-url-input',
                                    type='url',
                                    placeholder='https://...',
                                    style={
                                        'width': '100%',
                                        'backgroundColor': 'rgba(255,255,255,0.1)',
                                        'border': '1px solid rgba(255,255,255,0.3)',
                                        'borderRadius': '4px',
                                        'padding': '8px 12px',
                                        'color': 'white'
                                    }
                                )
                            ], md=6, sm=12, className='mb-3'),
                            dbc.Col([
                                html.Label("Your Email (optional, for follow-up):", className='filter-label', style={'color': 'rgba(255,255,255,0.9)'}),
                                dcc.Input(
                                    id='error-email-input',
                                    type='email',
                                    placeholder='your@email.com',
                                    style={
                                        'width': '100%',
                                        'backgroundColor': 'rgba(255,255,255,0.1)',
                                        'border': '1px solid rgba(255,255,255,0.3)',
                                        'borderRadius': '4px',
                                        'padding': '8px 12px',
                                        'color': 'white'
                                    }
                                )
                            ], md=6, sm=12, className='mb-3'),
                        ]),

                        html.Div([
                            html.Button("Submit Report", id='error-submit-btn',
                                       className='btn-export', n_clicks=0,
                                       style={'width': 'auto', 'marginTop': '10px', 'backgroundColor': 'white', 'color': COLORS['accent']})
                        ], style={'textAlign': 'center'}),

                        # Feedback area
                        html.Div(id='error-submit-feedback', style={'marginTop': '15px', 'textAlign': 'center'}),

                        # Privacy note
                        html.Div([
                            html.Small([
                                "Your privacy matters: Email is optional and only used if we need clarification. ",
                                "We do not share your information with third parties."
                            ], style={'color': 'rgba(255,255,255,0.7)', 'fontStyle': 'italic'})
                        ], style={'marginTop': '20px', 'textAlign': 'center'})

                    ], style={
                        'backgroundColor': 'rgba(0,0,0,0.2)',
                        'padding': '20px',
                        'borderRadius': '8px',
                        'marginTop': '10px'
                    })
                ], style={
                    'backgroundColor': COLORS['accent'],
                    'color': 'white',
                    'padding': '25px',
                    'borderRadius': '8px',
                    'textAlign': 'left'
                })
            ], className='container')
        ])
    ], className='methodology-container')


# ============================================
# APP LAYOUT
# ============================================

app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0, user-scalable=yes">
        <meta name="theme-color" content="#e94560">
        <meta name="apple-mobile-web-app-capable" content="yes">
        <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
        <link rel="manifest" href="/assets/manifest.json">
        <script src="https://html2canvas.hertzen.com/dist/html2canvas.min.js"></script>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
        <script>
            // Register Service Worker for PWA
            if ('serviceWorker' in navigator) {
                navigator.serviceWorker.register('/assets/sw.js')
                    .then(reg => console.log('SW registered'))
                    .catch(err => console.log('SW registration failed'));
            }
        </script>
    </body>
</html>
'''

app.layout = html.Div([
    # Header with dynamic background based on active tab
    html.Div([
        html.Div([
            html.H1("THE COST OF ENFORCEMENT", className='main-title'),
            html.P("An Interactive Investigation into U.S. Immigration Detention & Deportation",
                   className='subtitle'),
            html.Hr(className='title-rule'),
            html.P([
                "Data compiled from ",
                html.A("ICE Statistics", href="https://www.ice.gov/statistics", target="_blank"),
                ", ",
                html.A("American Immigration Council", href="https://www.americanimmigrationcouncil.org", target="_blank"),
                ", ",
                html.A("ACLU", href="https://www.aclu.org", target="_blank"),
                ", ",
                html.A("Deportation Data Project", href="https://deportationdata.org", target="_blank"),
                ", and other sources."
            ], className='source-note'),
            # Data freshness indicator
            html.Div(id='freshness-indicator', className='freshness-indicator', style={'marginTop': '15px'})
        ], className='header-content')
    ], id='header-section', className='header header-overview'),

    # Key Statistics Banner
    html.Div([
        html.Div([
            html.H3("THE NUMBERS", className='section-label'),
            dbc.Row([
                dbc.Col(create_key_stat_card("$170B", "2025 Budget", "Largest ever allocated"), md=2),
                dbc.Col(create_key_stat_card("73,000", "Currently Detained", "Record high"), md=2),
                dbc.Col(create_key_stat_card("73%", "No Criminal Record", "Of all detainees"), md=2),
                dbc.Col(create_key_stat_card("32", "Deaths in 2025", "3x previous year"), md=2),
                dbc.Col(create_key_stat_card("765%", "Budget Increase", "Since 1994 (adj.)"), md=2),
                dbc.Col(create_key_stat_card("$70,236", "Cost Per Deportation", "Average estimate"), md=2),
            ], className='stat-row'),
        ], className='container-fluid')
    ], className='stats-banner'),

    # Navigation Tabs
    html.Div([
        dbc.Tabs([
            dbc.Tab(label="Redacted", tab_id="tab-landing"),
            dbc.Tab(label="Overview", tab_id="tab-overview"),
            dbc.Tab(label="Funding & Budget", tab_id="tab-funding"),
            dbc.Tab(label="Detention", tab_id="tab-detention"),
            dbc.Tab(label="Deportations", tab_id="tab-deportations"),
            dbc.Tab(label="Deaths & Abuse", tab_id="tab-deaths"),
            dbc.Tab(label="Costs & Profits", tab_id="tab-costs"),
            dbc.Tab(label="Flight Tracker", tab_id="tab-flights"),
            dbc.Tab(label="Your Cost", tab_id="tab-calculator"),
            dbc.Tab(label="Timeline", tab_id="tab-timeline"),
            dbc.Tab(label="Map", tab_id="tab-map"),
            dbc.Tab(label="Facilities", tab_id="tab-facilities"),
            dbc.Tab(label="Legislation", tab_id="tab-legislation"),
            dbc.Tab(label="Data Explorer", tab_id="tab-explorer"),
            dbc.Tab(label="Narratives", tab_id="tab-narratives"),
            dbc.Tab(label="Resources", tab_id="tab-resources"),
            dbc.Tab(label="Methodology", tab_id="tab-methodology"),
        ], id="tabs", active_tab="tab-overview", className='nav-tabs-custom')
    ], className='nav-container'),

    # Main Content Area
    html.Div(id='tab-content', className='main-content'),

    # Footer
    html.Div([
        html.Div([
            html.Hr(className='footer-rule'),
            html.P([
                html.Strong("Data Sources: "),
                "ICE Official Statistics, American Immigration Council, ACLU, CATO Institute, ",
                "Brennan Center, Prison Policy Initiative, Freedom for Immigrants, ",
                "Physicians for Human Rights, Migration Policy Institute, Deportation Data Project, ",
                "USAFacts, The Guardian, CBS News, Penn Wharton Budget Model"
            ], className='footer-sources'),
            html.P(id='footer-disclaimer', children=[
                "This dashboard is for informational purposes. Data represents publicly available information ",
                "compiled from multiple sources. Last updated: January 2026."
            ], className='footer-disclaimer'),
        ], className='container')
    ], className='footer'),

    # Fixed Share Bar (privacy-focused sharing)
    html.Div([
        html.Button(
            "",
            id='fixed-share-signal',
            className='fixed-share-btn signal',
            title='Share via Signal (E2E encrypted)'
        ),
        html.A(
            "",
            id='fixed-share-telegram',
            className='fixed-share-btn telegram',
            href='https://t.me/share/url?url=https%3A%2F%2Fice-data-explorer.onrender.com&text=ICE%20Data%20Explorer%20-%20Interactive%20investigation%20into%20U.S.%20immigration%20enforcement',
            target='_blank',
            title='Share via Telegram (E2E encrypted)'
        ),
        html.A(
            "",
            id='fixed-share-whatsapp',
            className='fixed-share-btn whatsapp',
            href='https://wa.me/?text=ICE%20Data%20Explorer%20-%20Interactive%20investigation%20into%20U.S.%20immigration%20enforcement%20https%3A%2F%2Fice-data-explorer.onrender.com',
            target='_blank',
            title='Share via WhatsApp (E2E encrypted)'
        ),
        html.Button(
            "",
            id='fixed-share-copy',
            className='fixed-share-btn copy',
            title='Copy link to clipboard'
        ),
    ], className='fixed-share-bar'),

    # Clipboard for sharing
    dcc.Clipboard(id='main-clipboard', style={'display': 'none'}),

    # Store for share content
    dcc.Store(id='share-content-store', data={
        'title': 'The Cost of Enforcement',
        'description': 'Interactive investigation into U.S. immigration detention & deportation',
        'url': 'https://ice-data-explorer.onrender.com'
    }),
], className='app-container')


# ============================================
# CALLBACKS
# ============================================

@callback(
    Output('header-section', 'className'),
    Input('tabs', 'active_tab')
)
def update_header_background(active_tab):
    """Update header background image based on active tab."""
    tab_to_class = {
        'tab-landing': 'header header-overview',
        'tab-overview': 'header header-overview',
        'tab-funding': 'header header-funding',
        'tab-detention': 'header header-detention',
        'tab-deportations': 'header header-deportations',
        'tab-deaths': 'header header-deaths',
        'tab-costs': 'header header-costs',
        'tab-flights': 'header header-deportations',
        'tab-calculator': 'header header-costs',
        'tab-timeline': 'header header-timeline',
        'tab-map': 'header header-detention',
        'tab-facilities': 'header header-deaths',
        'tab-legislation': 'header header-funding',
        'tab-explorer': 'header header-explorer',
        'tab-narratives': 'header header-deaths',
        'tab-resources': 'header header-funding',
        'tab-methodology': 'header header-funding',
    }
    return tab_to_class.get(active_tab, 'header header-overview')


@callback(
    Output('freshness-indicator', 'children'),
    Input('tabs', 'active_tab')
)
def update_freshness_indicator(active_tab):
    """Update data freshness indicator."""
    sources = get_data_freshness()
    if not sources:
        return []

    # Calculate overall freshness
    fresh_count = sum(1 for s in sources if calculate_freshness_status(s['last_updated']) == 'fresh')
    total = len(sources)
    freshness = 'fresh' if fresh_count > total * 0.7 else 'recent' if fresh_count > total * 0.3 else 'stale'

    return [
        html.Span(className=f'freshness-dot freshness-{freshness}'),
        html.Span(f"Data from {total} sources • Last update: Jan 2026")
    ]


@callback(
    Output('tab-content', 'children'),
    Input('tabs', 'active_tab')
)
def render_tab_content(active_tab):
    """Render content for each tab."""

    if active_tab == 'tab-landing':
        return get_landing_content()

    elif active_tab == 'tab-overview':
        return html.Div([
            # Scrollytelling Mode Toggle Info
            html.Div([
                html.P([
                    "Scroll to explore the data, or click ",
                    html.Strong("Story Mode"),
                    " (top right) for a guided narrative experience."
                ], style={'textAlign': 'center', 'color': COLORS['text_muted'], 'fontSize': '0.9rem', 'marginBottom': '20px'})
            ], className='container'),

            # Lead paragraph with dramatic stat
            html.Div([
                html.P([
                    "In 2025, the United States allocated ",
                    html.Strong("$170 billion"),
                    " to immigration enforcement—more than the combined annual police budgets of all 50 states. ",
                    "The detention population has reached ",
                    html.Strong("73,000 people"),
                    ", the highest in ICE's 23-year history. ",
                    "Yet ",
                    html.Strong("73% of those detained have no criminal convictions"),
                    "."
                ], className='lead-paragraph')
            ], className='container'),

            # Story Section 1: The Money
            html.Div([
                html.Div([
                    html.Div("$170B", className='story-number'),
                    html.H2("The Largest Immigration Budget in History", className='story-headline'),
                    html.P([
                        "This single allocation exceeds the combined budgets of NASA, the EPA, ",
                        "and the Department of Education. It represents a 765% increase since 1994, ",
                        "adjusted for inflation."
                    ], className='story-text'),
                    html.Div([
                        dcc.Graph(figure=get_budget_chart(), config={'displayModeBar': False})
                    ], className='story-chart')
                ], className='story-content')
            ], className='story-section', **{'data-section-type': 'budget'}),

            # Story Section 2: The People
            html.Div([
                html.Div([
                    html.Div("73,000", className='story-number'),
                    html.H2("Record Detention Population", className='story-headline'),
                    html.P([
                        "More people are currently detained by ICE than at any point in the agency's ",
                        "23-year history. The population grew by 84% in a single year."
                    ], className='story-text'),
                    html.Div([
                        dcc.Graph(figure=get_detention_population_chart(), config={'displayModeBar': False})
                    ], className='story-chart')
                ], className='story-content')
            ], className='story-section', **{'data-section-type': 'detention'}),

            # Story Section 3: The Reality
            html.Div([
                html.Div([
                    html.Div("73%", className='story-number'),
                    html.H2("No Criminal Record", className='story-headline'),
                    html.P([
                        "Nearly three-quarters of those detained have no criminal convictions. ",
                        "They are being held for civil immigration violations, not crimes."
                    ], className='story-text'),
                    html.Div([
                        dcc.Graph(figure=get_criminal_status_chart(), config={'displayModeBar': False})
                    ], className='story-chart')
                ], className='story-content')
            ], className='story-section', **{'data-section-type': 'detention'}),

            # Story Section 4: The Human Cost
            html.Div([
                html.Div([
                    html.Div("32", className='story-number', style={'color': COLORS['danger']}),
                    html.H2("Deaths in ICE Custody (2025)", className='story-headline'),
                    html.P([
                        "2025 became the deadliest year in two decades. ",
                        "A joint ACLU/Physicians for Human Rights report found that ",
                        "95% of these deaths could have been prevented with adequate medical care."
                    ], className='story-text'),
                    html.Div([
                        dcc.Graph(figure=get_deaths_chart(), config={'displayModeBar': False})
                    ], className='story-chart')
                ], className='story-content')
            ], className='story-section deaths-content', **{'data-section-type': 'deaths'}),

            # Pull quote
            html.Div([
                html.Blockquote([
                    html.P('"The $170 billion price tag for immigration enforcement eclipses other law enforcement '
                           'expenditures at the federal, state, and local level. It is more than the annual expenditures '
                           'on police by state and local governments in all 50 states and the District of Columbia combined."'),
                    html.Footer("— Brennan Center for Justice", className='quote-source')
                ], className='pull-quote')
            ], className='container'),

            # Section indicators for scrollytelling
            html.Div([
                html.Div(className='section-dot', **{'data-section': '1'}),
                html.Div(className='section-dot', **{'data-section': '2'}),
                html.Div(className='section-dot', **{'data-section': '3'}),
                html.Div(className='section-dot', **{'data-section': '4'}),
            ], className='section-indicators', id='section-dots'),
        ], className='scrollytelling-container')

    elif active_tab == 'tab-funding':
        return html.Div([
            html.Div([
                html.H2("The Explosion of Immigration Enforcement Spending", className='section-title'),
                html.P([
                    "Since 1994, the Border Patrol budget has increased by ",
                    html.Strong("765% (inflation-adjusted)"),
                    ". ICE's budget has nearly tripled since its creation in 2003. ",
                    "The 2025 allocation of $170 billion represents an unprecedented expansion."
                ], className='section-intro')
            ], className='container'),

            dbc.Row([
                dbc.Col([
                    dcc.Graph(figure=get_budget_chart(), config={'displayModeBar': False})
                ], md=12),
            ], className='chart-row'),

            dbc.Row([
                dbc.Col([
                    dcc.Graph(figure=get_2025_allocation_chart(), config={'displayModeBar': False})
                ], md=6),
                dbc.Col([
                    html.Div([
                        html.H4("2025 Budget Highlights", className='info-card-title'),
                        html.Ul([
                            html.Li([html.Strong("$45 billion"), " for new detention centers (265% increase)"]),
                            html.Li([html.Strong("$29.9 billion"), " for enforcement & deportation (3x annual budget)"]),
                            html.Li([html.Strong("$46 billion"), " for border wall and infrastructure"]),
                            html.Li([html.Strong("$75 billion"), " total to ICE alone"]),
                        ], className='info-list'),
                        html.P([
                            "This makes ICE the ",
                            html.Strong("highest-funded law enforcement agency"),
                            " in the federal government."
                        ], className='info-note')
                    ], className='info-card')
                ], md=6),
            ], className='chart-row'),
        ])

    elif active_tab == 'tab-detention':
        return html.Div([
            html.Div([
                html.H2("Detention: Record Numbers, Unprecedented Growth", className='section-title'),
                html.P([
                    "The ICE detention population increased by ",
                    html.Strong("84%"),
                    " in one year, reaching ",
                    html.Strong("73,000 people"),
                    "—the highest in the agency's history. The number of people detained without any criminal record ",
                    "grew by ",
                    html.Strong("12,000%"),
                    " between January and June 2025."
                ], className='section-intro')
            ], className='container'),

            dbc.Row([
                dbc.Col([
                    dcc.Graph(figure=get_detention_population_chart(), config={'displayModeBar': False})
                ], md=12),
            ], className='chart-row'),

            dbc.Row([
                dbc.Col([
                    dcc.Graph(figure=get_criminal_status_chart(), config={'displayModeBar': False})
                ], md=6),
                dbc.Col([
                    dcc.Graph(figure=get_arrests_by_state_chart(), config={'displayModeBar': False})
                ], md=6),
            ], className='chart-row'),

            html.Div([
                html.H4("State-by-State: The Power of Policy", className='info-card-title'),
                html.P([
                    "States with sanctuary policies show significantly lower ICE arrest rates. ",
                    "Oregon (13.2 per 100k) and Illinois (21.0 per 100k) contrast sharply with ",
                    "Texas (110.0 per 100k) and Florida (58.2 per 100k)."
                ], className='info-note'),
            ], className='container info-card'),
        ])

    elif active_tab == 'tab-deportations':
        return html.Div([
            html.Div([
                html.H2("Deportations: A Historical View", className='section-title'),
                html.P([
                    "Through October 2025, DHS reported ",
                    html.Strong("527,000 deportations"),
                    ", with ICE averaging ",
                    html.Strong("965 arrests per day"),
                    ". The majority of those deported are Mexican nationals (51.8%), followed by Guatemalans (17.2%) ",
                    "and Hondurans (12.1%)."
                ], className='section-intro')
            ], className='container'),

            dbc.Row([
                dbc.Col([
                    dcc.Graph(figure=get_deportations_chart(), config={'displayModeBar': False})
                ], md=12),
            ], className='chart-row'),
        ])

    elif active_tab == 'tab-deaths':
        return html.Div([
            html.Div([
                html.H2("Deaths and Abuse in Detention", className='section-title'),
                html.P([
                    "2025 saw ",
                    html.Strong("32 deaths"),
                    " in ICE custody—the deadliest year since 2004 and nearly ",
                    html.Strong("3x the 2024 death toll"),
                    ". A joint ACLU/Physicians for Human Rights report found that ",
                    html.Strong("95% of deaths"),
                    " could have been prevented with adequate medical care."
                ], className='section-intro')
            ], className='container'),

            dbc.Row([
                dbc.Col([
                    dcc.Graph(figure=get_deaths_chart(), config={'displayModeBar': False})
                ], md=12),
            ], className='chart-row'),

            html.Div([
                html.H4("Documented Abuses", className='info-card-title'),
                html.P("Reports from ACLU, Human Rights Watch, and internal inspections have documented:", className='info-note'),
                html.Ul([
                    html.Li([html.Strong("Medical neglect"), " — Most common complaint from detainees"]),
                    html.Li([html.Strong("Physical abuse"), " — Beatings by officers documented at multiple facilities"]),
                    html.Li([html.Strong("Sexual abuse"), " — Staff sexual abuse of detainees reported"]),
                    html.Li([html.Strong("Coercive threats"), " — Threats used to compel deportation"]),
                    html.Li([html.Strong("Denial of counsel"), " — Systematic barriers to legal representation"]),
                    html.Li([html.Strong("60+ violations"), " — Fort Bliss violated federal standards in first 50 days"]),
                ], className='info-list'),
            ], className='container info-card'),
        ])

    elif active_tab == 'tab-costs':
        return html.Div([
            html.Div([
                html.H2("Following the Money", className='section-title'),
                html.P([
                    "ICE spends more than ",
                    html.Strong("$10 million per day"),
                    " on detention alone. The cost per deportation ranges from $17,000 (ICE estimate) to over $100,000 ",
                    "(independent analyses). Over 90% of detainees are held in privately-run facilities, generating ",
                    html.Strong("billions in revenue"),
                    " for companies like GEO Group and CoreCivic."
                ], className='section-intro')
            ], className='container'),

            dbc.Row([
                dbc.Col([
                    dcc.Graph(figure=get_cost_comparison_chart(), config={'displayModeBar': False})
                ], md=6),
                dbc.Col([
                    dcc.Graph(figure=get_private_prison_chart(), config={'displayModeBar': False})
                ], md=6),
            ], className='chart-row'),

            html.Div([
                html.H4("Cost Breakdown", className='info-card-title'),
                html.Table([
                    html.Thead(html.Tr([html.Th("Cost Type"), html.Th("Amount")])),
                    html.Tbody([
                        html.Tr([html.Td("Daily detention per person"), html.Td("~$150")]),
                        html.Tr([html.Td("County jail bed rate"), html.Td("$90-$120/day")]),
                        html.Tr([html.Td("Charter deportation flight"), html.Td("Up to $800,000")]),
                        html.Tr([html.Td("ICE Health Services (FY2025)"), html.Td("$360 million")]),
                        html.Tr([html.Td("Daily total detention spending"), html.Td("$10+ million")]),
                    ])
                ], className='cost-table'),
            ], className='container info-card'),
        ])

    elif active_tab == 'tab-flights':
        return html.Div([
            html.Div([
                html.H2("ICE Air Deportation Flight Tracker", className='section-title'),
                html.P([
                    "ICE Air Operations (IAO) conducts deportation flights daily from locations across the U.S. ",
                    "to countries throughout Latin America, the Caribbean, and beyond. ",
                    "This visualization shows simulated flight activity based on publicly known routes."
                ], className='section-intro')
            ], className='container'),

            # Flight Tracker
            html.Div([
                html.Div([
                    html.H3("Live Flight Activity", className='flight-tracker-title'),
                    html.Div([
                        html.Span(className='live-dot'),
                        html.Span("LIVE SIMULATION")
                    ], className='live-indicator')
                ], className='flight-tracker-header'),

                dcc.Graph(figure=get_flight_tracker_map(), config={'displayModeBar': False, 'scrollZoom': False}),

                html.Div(id='flight-stats-container', children=get_flight_stats_display()),
            ], className='container flight-tracker-container'),

            # Flight Information
            html.Div([
                html.H4("About ICE Air Operations", className='info-card-title'),
                html.P([
                    "ICE Air Operations is managed by ", html.Strong("Classic Air Charter"),
                    " and ", html.Strong("World Atlantic Airlines"),
                    ". Key hubs include:"
                ]),
                html.Ul([
                    html.Li([html.Strong("Mesa, AZ"), " — Primary hub for Mexico/Central America flights"]),
                    html.Li([html.Strong("Alexandria, LA"), " — Southern deportation processing center"]),
                    html.Li([html.Strong("San Antonio, TX"), " — High-volume Texas operations"]),
                    html.Li([html.Strong("Miami, FL"), " — Caribbean and South American deportations"]),
                ], className='info-list'),
                html.P([
                    "Charter flights can cost up to ", html.Strong("$800,000 per flight"),
                    " and carry 100-135 passengers. In FY2025, ICE Air conducted an estimated ",
                    html.Strong("4,500+ deportation flights"), "."
                ], className='info-note', style={'marginTop': '15px'})
            ], className='container info-card'),
        ])

    elif active_tab == 'tab-calculator':
        return get_taxpayer_receipt_content()

    elif active_tab == 'tab-timeline':
        # Get timeline data
        articles = query_data('''
            SELECT date, headline, source, url, category, sentiment_score, sentiment_label, summary, image_url
            FROM news_articles
            ORDER BY date DESC
        ''')
        stats = get_sentiment_trend_stats()

        # Calculate sentiment distribution percentages
        total = stats.get('total_articles', 1)
        very_neg_pct = (stats.get('very_negative', 0) / total) * 100
        neg_pct = (stats.get('negative', 0) / total) * 100
        neutral_pct = (stats.get('neutral', 0) / total) * 100
        pos_pct = (stats.get('positive', 0) / total) * 100

        return html.Div([
            html.Div([
                html.H2("News Timeline & Sentiment Analysis", className='section-title'),
                html.P([
                    "Tracking media coverage of ICE enforcement from ",
                    html.Strong("2024 to 2026"),
                    ". Sentiment analysis reveals overwhelmingly ",
                    html.Strong("negative coverage"),
                    f" with an average score of {stats.get('overall_avg', 0):.2f} across {total} articles analyzed."
                ], className='section-intro')
            ], className='container'),

            # Sentiment Summary Cards
            dbc.Row([
                dbc.Col([
                    create_key_stat_card(
                        f"{stats.get('overall_avg', 0):.2f}",
                        "Avg Sentiment",
                        "Overall coverage tone",
                        COLORS['accent']
                    )
                ], md=3),
                dbc.Col([
                    create_key_stat_card(
                        f"{very_neg_pct:.0f}%",
                        "Very Negative",
                        f"{stats.get('very_negative', 0)} articles",
                        COLORS['danger']
                    )
                ], md=3),
                dbc.Col([
                    create_key_stat_card(
                        f"{neg_pct:.0f}%",
                        "Negative",
                        f"{stats.get('negative', 0)} articles",
                        COLORS['accent']
                    )
                ], md=3),
                dbc.Col([
                    create_key_stat_card(
                        f"{pos_pct:.0f}%",
                        "Positive",
                        f"{stats.get('positive', 0)} articles",
                        COLORS['success']
                    )
                ], md=3),
            ], className='mb-4'),

            # Charts Row
            dbc.Row([
                dbc.Col([
                    dcc.Graph(figure=get_timeline_sentiment_chart(), config={'displayModeBar': False})
                ], md=8),
                dbc.Col([
                    dcc.Graph(figure=get_sentiment_by_category_chart(), config={'displayModeBar': False})
                ], md=4),
            ], className='chart-row'),

            # Trend Analysis
            html.Div([
                html.H4("Coverage Trend Analysis", className='info-card-title'),
                html.P([
                    "Analysis of ", html.Strong(f"{total} news articles"), " from major outlets reveals a consistently negative tone in ICE coverage. ",
                    "The most negative coverage centers on ", html.Strong("deaths in custody"),
                    " (avg score: -0.95) and ", html.Strong("abuse allegations"),
                    " (avg score: -0.90). The only category with positive sentiment is ",
                    html.Strong("policy analysis"), " showing sanctuary policies reducing arrest rates."
                ]),
                html.Hr(style={'borderColor': COLORS['grid']}),
                html.H5("Key Findings:", style={'color': COLORS['accent']}),
                html.Ul([
                    html.Li("Coverage became significantly more negative after January 2025 administration change"),
                    html.Li("Death-related coverage consistently receives the most negative sentiment scores"),
                    html.Li("Business/financial coverage (private prison profits) trends moderately negative"),
                    html.Li("Only 3% of analyzed coverage has positive sentiment"),
                ], style={'marginTop': '15px'})
            ], className='container info-card'),

            # Timeline Cards
            html.Div([
                html.H4("Article Timeline", className='info-card-title'),
                html.Div([
                    html.Div([
                        dbc.Row([
                            dbc.Col([
                                html.Img(
                                    src=article['image_url'],
                                    style={
                                        'width': '100%',
                                        'height': '120px',
                                        'objectFit': 'cover',
                                        'borderRadius': '4px',
                                        'opacity': '0.8'
                                    }
                                )
                            ], md=2),
                            dbc.Col([
                                html.Div([
                                    html.Span(
                                        article['sentiment_label'],
                                        style={
                                            'backgroundColor': COLORS['danger'] if article['sentiment_score'] <= -0.7
                                                else COLORS['accent'] if article['sentiment_score'] <= -0.4
                                                else COLORS['warning'] if article['sentiment_score'] <= 0
                                                else COLORS['success'],
                                            'color': 'white',
                                            'padding': '2px 8px',
                                            'borderRadius': '4px',
                                            'fontSize': '0.75rem',
                                            'marginRight': '10px'
                                        }
                                    ),
                                    html.Span(
                                        article['category'],
                                        style={
                                            'backgroundColor': COLORS['grid'],
                                            'color': COLORS['text'],
                                            'padding': '2px 8px',
                                            'borderRadius': '4px',
                                            'fontSize': '0.75rem'
                                        }
                                    ),
                                    html.Span(
                                        f" — {article['date']}",
                                        style={'color': COLORS['text_muted'], 'fontSize': '0.85rem', 'marginLeft': '10px'}
                                    )
                                ]),
                                html.H5(
                                    article['headline'],
                                    style={'margin': '8px 0', 'fontSize': '1.1rem'}
                                ),
                                html.P(
                                    article['summary'],
                                    style={'color': COLORS['text_muted'], 'fontSize': '0.9rem', 'marginBottom': '5px'}
                                ),
                                html.Small(
                                    f"Source: {article['source']} | Sentiment Score: {article['sentiment_score']:.2f}",
                                    style={'color': COLORS['text_muted']}
                                )
                            ], md=10)
                        ], style={
                            'padding': '15px',
                            'marginBottom': '10px',
                            'backgroundColor': 'rgba(255,255,255,0.02)',
                            'borderRadius': '8px',
                            'borderLeft': f"4px solid {COLORS['danger'] if article['sentiment_score'] <= -0.7 else COLORS['accent'] if article['sentiment_score'] <= -0.4 else COLORS['warning'] if article['sentiment_score'] <= 0 else COLORS['success']}"
                        })
                    ]) for article in articles[:15]  # Show latest 15 articles
                ])
            ], className='container info-card'),
        ])

    elif active_tab == 'tab-map':
        return html.Div([
            html.Div([
                html.H2("Geographic Analysis", className='section-title'),
                html.P([
                    "Visualize the geographic distribution of ICE enforcement. ",
                    "Detention facilities are concentrated in the South and Southwest, ",
                    "with the largest populations in Texas, Louisiana, and Arizona."
                ], className='section-intro')
            ], className='container'),

            # Facilities Map
            html.Div([
                dcc.Graph(figure=get_facilities_map(), config={'displayModeBar': False, 'scrollZoom': False})
            ], className='map-container'),

            # Map Legend
            html.Div([
                html.Div([
                    html.Span(className='legend-dot', style={'background': COLORS['accent']}),
                    html.Span("GEO Group")
                ], className='legend-item'),
                html.Div([
                    html.Span(className='legend-dot', style={'background': COLORS['blue']}),
                    html.Span("CoreCivic")
                ], className='legend-item'),
                html.Div([
                    html.Span(className='legend-dot', style={'background': COLORS['purple']}),
                    html.Span("ICE-operated")
                ], className='legend-item'),
                html.Div([
                    html.Span(className='legend-dot', style={'background': COLORS['warning']}),
                    html.Span("LaSalle Corrections")
                ], className='legend-item'),
                html.Div([
                    html.Span(className='legend-dot', style={'background': COLORS['success']}),
                    html.Span("Other")
                ], className='legend-item'),
            ], className='map-legend container'),

            # Arrests Rate Map
            html.Div([
                html.H4("Arrest Rates by State", className='info-card-title'),
                dcc.Graph(figure=get_arrests_map(), config={'displayModeBar': False, 'scrollZoom': False})
            ], className='container info-card', style={'marginTop': '30px'}),
        ])

    elif active_tab == 'tab-facilities':
        # Get facilities data
        facilities = query_data('''
            SELECT * FROM detention_facilities
            WHERE current_population > 0
            ORDER BY current_population DESC
        ''')

        return html.Div([
            html.Div([
                html.H2("Facility Deep Dive", className='section-title'),
                html.P([
                    "Detailed information on ICE detention facilities including capacity, deaths, complaints, ",
                    "and inspection scores. Click on any facility to see more details and take action."
                ], className='section-intro')
            ], className='container'),

            # Summary stats
            dbc.Row([
                dbc.Col(create_key_stat_card(
                    f"{len(facilities)}",
                    "Active Facilities",
                    "Currently operating"
                ), md=3),
                dbc.Col(create_key_stat_card(
                    f"{sum(f['current_population'] for f in facilities):,}",
                    "Total Detained",
                    "Across all facilities"
                ), md=3),
                dbc.Col(create_key_stat_card(
                    f"{sum(f['deaths_total'] for f in facilities)}",
                    "Total Deaths",
                    "Documented since opening"
                ), md=3),
                dbc.Col(create_key_stat_card(
                    f"{sum(f['complaints_total'] for f in facilities):,}",
                    "Total Complaints",
                    "Filed against facilities"
                ), md=3),
            ], className='mb-4'),

            # Take Action Section
            html.Div([
                html.H4("Take Action - Report Issues & Contact Representatives", className='info-card-title'),
                html.P("If you have concerns about detention conditions, you can contact these resources:",
                       style={'color': COLORS['text_muted'], 'marginBottom': '20px'}),
                dbc.Row([
                    dbc.Col([
                        html.Div([
                            html.H5("ICE Detention Reporting", style={'color': COLORS['accent']}),
                            html.P("Report civil rights violations directly to DHS", style={'fontSize': '0.9rem', 'color': COLORS['text_muted']}),
                            html.A(
                                html.Button("Call: 1-877-2-ICE-TIP", className='btn-export', style={'marginRight': '10px'}),
                                href="tel:1-877-246-8477"
                            ),
                            html.A(
                                html.Button("Email DHS CRCL", className='btn-export-small', style={'marginTop': '10px', 'display': 'block'}),
                                href="mailto:CRCLCompliance@hq.dhs.gov"
                            )
                        ], style={'padding': '15px', 'background': 'rgba(255,255,255,0.03)', 'borderRadius': '8px'})
                    ], md=4),
                    dbc.Col([
                        html.Div([
                            html.H5("ACLU Immigrant Rights", style={'color': COLORS['blue']}),
                            html.P("Document and report abuse", style={'fontSize': '0.9rem', 'color': COLORS['text_muted']}),
                            html.A(
                                html.Button("Report to ACLU", className='btn-export'),
                                href="https://www.aclu.org/report-ice-detention-abuse", target="_blank"
                            ),
                            html.A(
                                html.Button("Freedom for Immigrants Hotline", className='btn-export-small', style={'marginTop': '10px', 'display': 'block'}),
                                href="tel:1-209-757-3733"
                            )
                        ], style={'padding': '15px', 'background': 'rgba(255,255,255,0.03)', 'borderRadius': '8px'})
                    ], md=4),
                    dbc.Col([
                        html.Div([
                            html.H5("Contact Your Representatives", style={'color': COLORS['success']}),
                            html.P("Find and contact your elected officials", style={'fontSize': '0.9rem', 'color': COLORS['text_muted']}),
                            html.A(
                                html.Button("Find Your Senator", className='btn-export'),
                                href="https://www.senate.gov/senators/senators-contact.htm", target="_blank"
                            ),
                            html.A(
                                html.Button("Find Your Representative", className='btn-export-small', style={'marginTop': '10px', 'display': 'block'}),
                                href="https://www.house.gov/representatives/find-your-representative", target="_blank"
                            )
                        ], style={'padding': '15px', 'background': 'rgba(255,255,255,0.03)', 'borderRadius': '8px'})
                    ], md=4),
                ]),
                html.Hr(style={'borderColor': COLORS['grid'], 'marginTop': '25px'}),
                html.P([
                    html.Strong("Legal Aid Resources: "),
                    html.A("RAICES", href="https://www.raicestexas.org", target="_blank", style={'color': COLORS['accent']}),
                    " | ",
                    html.A("NIJC", href="https://immigrantjustice.org", target="_blank", style={'color': COLORS['accent']}),
                    " | ",
                    html.A("CLINIC", href="https://cliniclegal.org", target="_blank", style={'color': COLORS['accent']}),
                    " | ",
                    html.A("Immigration Advocates Network", href="https://www.immigrationadvocates.org/nonprofit/legaldirectory/", target="_blank", style={'color': COLORS['accent']})
                ], style={'fontSize': '0.9rem', 'color': COLORS['text_muted']})
            ], className='container info-card'),

            # Facility cards
            html.Div([
                html.H4("All Facilities", className='info-card-title'),
                html.Div([
                    html.Div([
                        html.Div([
                            html.Div([
                                html.H5(f['name'], className='facility-name'),
                                html.P(f"{f['city']}, {f['state']}", className='facility-location')
                            ]),
                            html.Span(
                                f['operator'].split()[0] if f['operator'] else 'Unknown',
                                className=f"facility-badge badge-{'geo' if 'GEO' in (f['operator'] or '') else 'corecivic' if 'CoreCivic' in (f['operator'] or '') else 'ice' if 'ICE' in (f['operator'] or '') else 'other'}"
                            )
                        ], className='facility-header'),
                        html.Div([
                            html.Div([
                                html.Div(f"{f['current_population']:,}", className='facility-stat-value'),
                                html.Div("Population", className='facility-stat-label')
                            ], className='facility-stat'),
                            html.Div([
                                html.Div(f"{f['capacity']:,}", className='facility-stat-value', style={'color': COLORS['text_muted']}),
                                html.Div("Capacity", className='facility-stat-label')
                            ], className='facility-stat'),
                            html.Div([
                                html.Div(f"{(f['current_population']/f['capacity']*100):.0f}%", className='facility-stat-value',
                                        style={'color': COLORS['danger'] if f['current_population']/f['capacity'] > 0.95 else COLORS['warning'] if f['current_population']/f['capacity'] > 0.8 else COLORS['success']}),
                                html.Div("Occupancy", className='facility-stat-label')
                            ], className='facility-stat'),
                            html.Div([
                                html.Div(str(f['deaths_total']), className='facility-stat-value', style={'color': COLORS['danger'] if f['deaths_total'] > 2 else COLORS['text']}),
                                html.Div("Deaths", className='facility-stat-label')
                            ], className='facility-stat'),
                            html.Div([
                                html.Div(str(f['complaints_total']), className='facility-stat-value'),
                                html.Div("Complaints", className='facility-stat-label')
                            ], className='facility-stat'),
                            html.Div([
                                html.Div(f"${f['per_diem_rate']:.0f}", className='facility-stat-value', style={'color': COLORS['warning']}),
                                html.Div("Per Diem", className='facility-stat-label')
                            ], className='facility-stat'),
                        ], className='facility-stats'),
                        html.Div([
                            html.Span(
                                f"Inspection: {f['inspection_score']}",
                                style={
                                    'padding': '4px 10px',
                                    'borderRadius': '4px',
                                    'fontSize': '0.8rem',
                                    'background': COLORS['danger'] if f['inspection_score'] == 'Deficient' else COLORS['success'] if f['inspection_score'] == 'Acceptable' else COLORS['grid'],
                                    'color': 'white'
                                }
                            ),
                            html.Span(f" • Last inspection: {f['last_inspection_date']}", style={'color': COLORS['text_muted'], 'fontSize': '0.85rem', 'marginLeft': '10px'}),
                            html.Span(f" • {f['notes']}" if f['notes'] else "", style={'color': COLORS['text_muted'], 'fontSize': '0.85rem', 'marginLeft': '10px'})
                        ], style={'marginTop': '15px'})
                    ], className=f"facility-card {'deficient' if f['inspection_score'] == 'Deficient' else 'acceptable'}")
                    for f in facilities[:20]  # Show top 20
                ])
            ], className='container info-card'),
        ])

    elif active_tab == 'tab-legislation':
        # Get legislation data
        bills = query_data('SELECT * FROM legislation ORDER BY last_action_date DESC')

        # Count by status
        status_counts = {}
        for b in bills:
            status = b['status']
            status_counts[status] = status_counts.get(status, 0) + 1

        total_funding = sum(b['funding_amount'] or 0 for b in bills if b['funding_amount'])

        return html.Div([
            html.Div([
                html.H2("Legislative Tracker", className='section-title'),
                html.P([
                    "Track immigration-related bills, their sponsors, status, and funding allocations. ",
                    "The 2025 legislative session saw historic funding increases for immigration enforcement."
                ], className='section-intro')
            ], className='container'),

            # Summary stats
            dbc.Row([
                dbc.Col(create_key_stat_card(
                    str(len(bills)),
                    "Bills Tracked",
                    "Immigration-related"
                ), md=3),
                dbc.Col(create_key_stat_card(
                    str(status_counts.get('Signed into Law', 0) + status_counts.get('Passed House', 0) + status_counts.get('Passed Senate', 0)),
                    "Bills Advancing",
                    "Passed at least one chamber"
                ), md=3),
                dbc.Col(create_key_stat_card(
                    f"${total_funding/1e9:.0f}B",
                    "Total Funding",
                    "In tracked bills"
                ), md=3),
                dbc.Col(create_key_stat_card(
                    "H.R.7921",
                    "Largest Bill",
                    "$170B enforcement package"
                ), md=3),
            ], className='mb-4'),

            # Contact Representatives CTA
            html.Div([
                html.H4("Voice Your Opinion on Pending Legislation", className='info-card-title'),
                dbc.Row([
                    dbc.Col([
                        html.P("Contact your elected representatives to share your views on immigration legislation:",
                               style={'color': COLORS['text_muted']}),
                    ], md=6),
                    dbc.Col([
                        html.A(
                            html.Button("Find Your Senator", className='btn-export', style={'marginRight': '10px'}),
                            href="https://www.senate.gov/senators/senators-contact.htm", target="_blank"
                        ),
                        html.A(
                            html.Button("Find Your Representative", className='btn-export'),
                            href="https://www.house.gov/representatives/find-your-representative", target="_blank"
                        ),
                    ], md=6, style={'textAlign': 'right'}),
                ]),
            ], className='container info-card'),

            # Bill cards
            html.Div([
                html.H4("Recent Legislation", className='info-card-title'),
                html.Div([
                    html.Div([
                        html.Div([
                            html.Span(b['bill_number'], className='bill-number'),
                            html.Span(
                                b['status'],
                                className=f"bill-status status-{'law' if 'Law' in b['status'] else 'passed' if 'Passed' in b['status'] else 'committee' if 'Committee' in b['status'] else 'failed'}"
                            )
                        ], className='bill-header'),
                        html.H5(b['title'], className='bill-title'),
                        html.P(b['description'], style={'color': COLORS['text_muted'], 'fontSize': '0.9rem'}),
                        html.Div([
                            html.Span(f"Sponsor: {b['sponsor']} ({b['party']})", style={'marginRight': '20px'}),
                            html.Span(f"Category: {b['category']}", style={'marginRight': '20px'}),
                            html.Span(f"Last Action: {b['last_action_date']}")
                        ], className='bill-meta'),
                        html.Div(f"${b['funding_amount']/1e9:.1f} Billion" if b['funding_amount'] else "", className='bill-funding'),
                        html.Div([
                            html.Span(f"House: {b['vote_house']}" if b['vote_house'] else "", style={'marginRight': '15px', 'color': COLORS['success'] if b['vote_house'] and 'Passed' in b['vote_house'] else COLORS['text_muted']}),
                            html.Span(f"Senate: {b['vote_senate']}" if b['vote_senate'] else "", style={'color': COLORS['success'] if b['vote_senate'] and 'Passed' in b['vote_senate'] else COLORS['text_muted']})
                        ], style={'marginTop': '10px', 'fontSize': '0.9rem'}),
                        html.P(b['impact_summary'], style={'marginTop': '10px', 'fontStyle': 'italic', 'color': COLORS['text_muted'], 'fontSize': '0.85rem'}) if b['impact_summary'] else None
                    ], className='bill-card')
                    for b in bills
                ])
            ], className='container info-card'),
        ])

    elif active_tab == 'tab-explorer':
        return html.Div([
            html.Div([
                html.H2("Data Explorer", className='section-title'),
                html.P("Explore immigration enforcement data interactively. Select a dataset, filter, visualize, and export.",
                       className='section-intro')
            ], className='container'),

            html.Div([
                # Row 1: Dataset Selection and Description
                dbc.Row([
                    dbc.Col([
                        html.Label("Select Dataset:", className='filter-label'),
                        dcc.Dropdown(
                            id='table-selector',
                            options=[
                                {'label': 'Agency Budgets (Historical)', 'value': 'agency_budgets'},
                                {'label': '2025 Budget Allocations', 'value': 'budget_allocations_2025'},
                                {'label': 'Detention Population', 'value': 'detention_population'},
                                {'label': 'Detention by State', 'value': 'detention_by_state'},
                                {'label': 'Deportations', 'value': 'deportations'},
                                {'label': 'Deportations by Nationality', 'value': 'deportations_by_nationality'},
                                {'label': 'Deaths in Custody', 'value': 'deaths_in_custody'},
                                {'label': 'Abuse Complaints', 'value': 'abuse_complaints'},
                                {'label': 'Deportation Costs', 'value': 'deportation_costs'},
                                {'label': 'Private Prison Contracts', 'value': 'private_prison_contracts'},
                                {'label': 'Staffing', 'value': 'staffing'},
                                {'label': 'Arrests', 'value': 'arrests'},
                                {'label': 'Arrests by State', 'value': 'arrests_by_state'},
                                {'label': 'Detainee Criminal Status', 'value': 'detainee_criminal_status'},
                                {'label': 'Key Statistics', 'value': 'key_statistics'},
                                {'label': 'News Articles', 'value': 'news_articles'},
                            ],
                            value='deportation_costs',
                            className='dropdown-custom'
                        )
                    ], md=4),
                    dbc.Col([
                        html.Label("Compare With (optional):", className='filter-label'),
                        dcc.Dropdown(
                            id='compare-selector',
                            options=[
                                {'label': 'None', 'value': ''},
                                {'label': 'Agency Budgets', 'value': 'agency_budgets'},
                                {'label': 'Detention Population', 'value': 'detention_population'},
                                {'label': 'Deportations', 'value': 'deportations'},
                                {'label': 'Deaths in Custody', 'value': 'deaths_in_custody'},
                                {'label': 'Private Prison Contracts', 'value': 'private_prison_contracts'},
                            ],
                            value='',
                            className='dropdown-custom',
                            placeholder='Select to compare...'
                        )
                    ], md=4),
                    dbc.Col([
                        html.Div(id='dataset-description', style={
                            'backgroundColor': 'rgba(233, 69, 96, 0.1)',
                            'padding': '10px 15px',
                            'borderRadius': '4px',
                            'borderLeft': f'3px solid {COLORS["accent"]}',
                            'fontSize': '0.9rem',
                            'color': COLORS['text_muted'],
                            'marginTop': '24px'
                        })
                    ], md=4),
                ], className='mb-3'),

                # Row 2: Filters
                dbc.Row([
                    dbc.Col([
                        html.Label("Filter by Year:", className='filter-label'),
                        dcc.Dropdown(
                            id='year-filter',
                            options=[],
                            value=None,
                            className='dropdown-custom',
                            placeholder='All years'
                        )
                    ], md=2),
                    dbc.Col([
                        html.Label("Search:", className='filter-label'),
                        dcc.Input(
                            id='search-filter',
                            type='text',
                            placeholder='Search all fields...',
                            className='input-custom'
                        )
                    ], md=3),
                    dbc.Col([
                        html.Label("Quick Filters:", className='filter-label'),
                        html.Div([
                            html.Button("2025", id='preset-2025', className='btn-preset', n_clicks=0),
                            html.Button("2024", id='preset-2024', className='btn-preset', n_clicks=0),
                            html.Button("Recent", id='preset-recent', className='btn-preset', n_clicks=0),
                            html.Button("Clear", id='preset-clear', className='btn-preset btn-preset-clear', n_clicks=0),
                        ], style={'display': 'flex', 'gap': '5px', 'flexWrap': 'wrap'})
                    ], md=4),
                    dbc.Col([
                        html.Label("Actions:", className='filter-label'),
                        html.Div([
                            html.Button("📊 Visualize", id='visualize-btn', className='btn-export', style={'marginRight': '5px'}),
                        ], style={'display': 'flex', 'gap': '5px'})
                    ], md=3),
                ], className='filter-row'),

                # Row 3: Summary Statistics
                html.Div(id='summary-stats-container', className='mb-3'),

                # Row 4: Visualization Area (hidden by default)
                html.Div(id='visualization-container', style={'display': 'none'}),

                # Row 5: Data Table
                html.Div(id='data-table-container', className='table-container'),

                # Row 6: Export Options
                dbc.Row([
                    dbc.Col([
                        html.Div([
                            html.Label("Export Data:", className='filter-label', style={'marginBottom': '5px'}),
                            html.Div([
                                html.Button("📥 CSV", id='export-csv-btn', className='btn-export-small'),
                                html.Button("📥 Excel", id='export-excel-btn', className='btn-export-small'),
                                html.Button("📥 JSON", id='export-json-btn', className='btn-export-small'),
                            ], style={'display': 'flex', 'gap': '10px'})
                        ])
                    ], md=12),
                ], className='mt-3'),

                dcc.Download(id='download-csv'),
                dcc.Download(id='download-excel'),
                dcc.Download(id='download-json'),
                dcc.Store(id='current-data-store'),
            ], className='container explorer-container'),
        ])

    elif active_tab == 'tab-narratives':
        return html.Div([
            # Sub-navigation for narrative pages
            html.Div([
                html.Div([
                    html.H2("Challenging the Narratives", className='section-title'),
                    html.P([
                        "Data-driven visualizations that challenge official rhetoric and reveal hidden truths."
                    ], className='section-intro'),
                ], className='container'),

                # Sub-tabs for different narratives
                html.Div([
                    dbc.Tabs([
                        dbc.Tab(label="Criminality Myth", tab_id="narrative-criminality"),
                        dbc.Tab(label="In Memoriam", tab_id="narrative-memorial"),
                        dbc.Tab(label="Abuse Archive", tab_id="narrative-abuse"),
                        dbc.Tab(label="Deportation Globe", tab_id="narrative-globe"),
                        dbc.Tab(label="Arrest Heatmap", tab_id="narrative-heatmap"),
                        dbc.Tab(label="Detention Map", tab_id="narrative-cartogram"),
                        dbc.Tab(label="Logistics Network", tab_id="narrative-logistics"),
                        dbc.Tab(label="Militarization", tab_id="narrative-isotype"),
                        dbc.Tab(label="Surveillance", tab_id="narrative-surveillance"),
                        dbc.Tab(label="Follow the Money", tab_id="narrative-sankey"),
                        dbc.Tab(label="Profit Correlation", tab_id="narrative-profit"),
                        dbc.Tab(label="Rigged Bidding", tab_id="narrative-bidding"),
                        dbc.Tab(label="Corporate Hydra", tab_id="narrative-hydra"),
                        dbc.Tab(label="Media Pulse", tab_id="narrative-media"),
                        dbc.Tab(label="Data Gaps", tab_id="narrative-gaps"),
                        dbc.Tab(label="Contested Stats", tab_id="narrative-bayesian"),
                    ], id="narrative-tabs", active_tab="narrative-criminality", className='nav-tabs-custom sub-tabs')
                ], className='container'),

                # Content area
                html.Div(id='narrative-content', className='narrative-content-area'),
            ], className='narratives-page-container')
        ])

    elif active_tab == 'tab-resources':
        return get_community_resources_content()

    elif active_tab == 'tab-methodology':
        return get_methodology_tab_content()

    return html.Div("Select a tab to view content.")


# ============================================
# PROVENANCE TABLE FILTER CALLBACK
# ============================================

@callback(
    Output('provenance-table-container', 'children'),
    Input('provenance-status-filter', 'value'),
    Input('provenance-source-filter', 'value'),
    Input('provenance-preset-verified', 'n_clicks'),
    Input('provenance-preset-hide-govt', 'n_clicks'),
    Input('provenance-preset-clear', 'n_clicks'),
)
def update_provenance_table(status_filter, source_type_filter, n_verified, n_hide_govt, n_clear):
    """Filter the data provenance table based on user selections."""
    from dash import ctx

    # Handle preset buttons
    triggered = ctx.triggered_id if ctx.triggered_id else None

    if triggered == 'provenance-preset-verified':
        status_filter = 'verified'
        source_type_filter = ''
    elif triggered == 'provenance-preset-hide-govt':
        status_filter = 'hide_government_only'  # Special value
        source_type_filter = ''
    elif triggered == 'provenance-preset-clear':
        status_filter = ''
        source_type_filter = ''

    # Build query with filters
    query = '''
        SELECT dp.*, sr.source_type
        FROM data_provenance dp
        LEFT JOIN source_registry sr ON dp.primary_source_id = sr.id
        WHERE 1=1
    '''
    params = []

    if status_filter == 'hide_government_only':
        query += " AND dp.verification_status != 'government_only'"
    elif status_filter:
        query += ' AND dp.verification_status = ?'
        params.append(status_filter)

    if source_type_filter:
        query += ' AND sr.source_type = ?'
        params.append(source_type_filter)

    query += ' ORDER BY dp.metric_category, dp.metric_name'

    provenance_data = query_data(query, params if params else None)

    return build_provenance_table(provenance_data)


# ============================================
# ERROR REPORTING FORM CALLBACK
# ============================================

@callback(
    Output('error-submit-feedback', 'children'),
    Input('error-submit-btn', 'n_clicks'),
    State('error-type-dropdown', 'value'),
    State('error-metric-input', 'value'),
    State('error-description-textarea', 'value'),
    State('error-source-url-input', 'value'),
    State('error-email-input', 'value'),
    prevent_initial_call=True
)
def submit_error_report(n_clicks, error_type, metric_name, description, source_url, email):
    """Submit an error report to the database."""
    if not n_clicks:
        return ""

    # Validation
    if not description or len(description.strip()) < 10:
        return html.Div([
            html.Span("⚠️ ", style={'marginRight': '5px'}),
            html.Span("Please provide a description of the issue (at least 10 characters).")
        ], style={'color': '#ffd166'})

    # Insert into database
    try:
        query = '''
            INSERT INTO error_reports (error_type, metric_name, description, suggested_source_url, reporter_email)
            VALUES (?, ?, ?, ?, ?)
        '''
        execute_query(query, (
            error_type,
            metric_name.strip() if metric_name else None,
            description.strip(),
            source_url.strip() if source_url else None,
            email.strip() if email else None
        ))

        return html.Div([
            html.Span("✓ ", style={'marginRight': '5px'}),
            html.Span("Thank you! Your report has been submitted. ", style={'fontWeight': 'bold'}),
            html.Span("We will review it and update our data if needed.")
        ], style={'color': '#06d6a0'})

    except Exception as e:
        return html.Div([
            html.Span("❌ ", style={'marginRight': '5px'}),
            html.Span("Sorry, there was an error submitting your report. Please try again later.")
        ], style={'color': '#ef476f'})


@callback(
    Output('dataset-description', 'children'),
    Input('table-selector', 'value')
)
def update_dataset_description(table_name):
    """Update the dataset description based on selection."""
    if not table_name:
        return "Select a dataset to see its description."
    return DATASET_DESCRIPTIONS.get(table_name, "No description available.")


@callback(
    Output('year-filter', 'options'),
    Output('year-filter', 'value'),
    Input('table-selector', 'value'),
    Input('preset-2025', 'n_clicks'),
    Input('preset-2024', 'n_clicks'),
    Input('preset-recent', 'n_clicks'),
    Input('preset-clear', 'n_clicks'),
)
def update_year_options(table_name, n_2025, n_2024, n_recent, n_clear):
    """Update year dropdown options based on selected table."""
    from dash import ctx

    years = get_available_years(table_name) if table_name else []
    options = [{'label': 'All Years', 'value': ''}] + [{'label': str(y), 'value': y} for y in years]

    # Handle preset buttons
    triggered = ctx.triggered_id if ctx.triggered_id else None

    if triggered == 'preset-2025' and 2025 in years:
        return options, 2025
    elif triggered == 'preset-2024' and 2024 in years:
        return options, 2024
    elif triggered == 'preset-recent' and years:
        return options, years[0]  # Most recent year
    elif triggered == 'preset-clear':
        return options, ''

    return options, ''


@callback(
    Output('summary-stats-container', 'children'),
    Input('table-selector', 'value'),
    Input('year-filter', 'value'),
)
def update_summary_stats(table_name, year_filter):
    """Generate summary statistics for the selected dataset."""
    if not table_name:
        return html.Div()

    # Get data
    query = f'SELECT * FROM {table_name}'
    params = []
    year_col = 'fiscal_year' if table_name in ['deportations', 'deportations_by_nationality'] else 'year'

    if year_filter:
        query += f' WHERE {year_col} = ?'
        params.append(year_filter)

    data = query_data(query, params if params else None)
    if not data:
        return html.Div()

    df = pd.DataFrame(data)
    record_count = len(df)

    # Find numeric columns for stats
    numeric_cols = CURRENCY_COLUMNS + NUMBER_COLUMNS
    stats = calculate_summary_stats(df, numeric_cols)

    if not stats:
        return html.Div([
            html.Span(f"📊 {record_count} records", style={
                'backgroundColor': COLORS['accent'],
                'color': 'white',
                'padding': '5px 12px',
                'borderRadius': '4px',
                'fontSize': '0.9rem'
            })
        ], style={'marginBottom': '15px'})

    # Build stats cards
    stat_items = [
        html.Span(f"📊 {record_count} records", style={
            'backgroundColor': COLORS['accent'],
            'color': 'white',
            'padding': '5px 12px',
            'borderRadius': '4px',
            'fontSize': '0.9rem',
            'marginRight': '10px'
        })
    ]

    # Show stats for first numeric column found
    for col, col_stats in list(stats.items())[:2]:
        label = get_column_label(col)
        if col in CURRENCY_COLUMNS:
            stat_items.append(html.Span([
                html.Strong(f"{label}: "),
                f"Avg {format_value(col_stats['avg'], col)} | ",
                f"Range {format_value(col_stats['min'], col)} - {format_value(col_stats['max'], col)}"
            ], style={
                'backgroundColor': COLORS['grid'],
                'padding': '5px 12px',
                'borderRadius': '4px',
                'fontSize': '0.85rem',
                'marginRight': '10px'
            }))
        elif col in NUMBER_COLUMNS:
            stat_items.append(html.Span([
                html.Strong(f"{label}: "),
                f"Total {format_value(col_stats['sum'], col)} | ",
                f"Avg {format_value(col_stats['avg'], col)}"
            ], style={
                'backgroundColor': COLORS['grid'],
                'padding': '5px 12px',
                'borderRadius': '4px',
                'fontSize': '0.85rem',
                'marginRight': '10px'
            }))

    return html.Div(stat_items, style={'marginBottom': '15px', 'display': 'flex', 'flexWrap': 'wrap', 'gap': '5px'})


@callback(
    Output('visualization-container', 'children'),
    Output('visualization-container', 'style'),
    Input('visualize-btn', 'n_clicks'),
    State('table-selector', 'value'),
    State('year-filter', 'value'),
    prevent_initial_call=True
)
def generate_visualization(n_clicks, table_name, year_filter):
    """Generate a visualization for the selected data."""
    if not n_clicks or not table_name:
        return html.Div(), {'display': 'none'}

    # Get data
    query = f'SELECT * FROM {table_name}'
    params = []
    year_col = 'fiscal_year' if table_name in ['deportations', 'deportations_by_nationality'] else 'year'

    if year_filter:
        query += f' WHERE {year_col} = ?'
        params.append(year_filter)

    data = query_data(query, params if params else None)
    if not data:
        return html.P("No data to visualize."), {'display': 'block'}

    df = pd.DataFrame(data)

    # Determine best chart type based on data
    fig = None

    # Time series data
    if 'year' in df.columns or 'fiscal_year' in df.columns:
        year_col = 'fiscal_year' if 'fiscal_year' in df.columns else 'year'

        # Find a numeric column to plot
        for col in ['budget_adjusted_millions', 'budget_millions', 'population', 'removals',
                    'deaths', 'revenue_millions', 'arrests', 'amount_dollars']:
            if col in df.columns:
                if 'agency' in df.columns or 'company' in df.columns:
                    color_col = 'agency' if 'agency' in df.columns else 'company'
                    fig = px.line(df, x=year_col, y=col, color=color_col,
                                  title=f'{get_column_label(col)} Over Time',
                                  markers=True)
                else:
                    fig = px.bar(df, x=year_col, y=col,
                                 title=f'{get_column_label(col)} by Year')
                break

    # State data
    elif 'state' in df.columns:
        for col in ['arrests_per_100k', 'total_arrests', 'population']:
            if col in df.columns:
                fig = px.bar(df.sort_values(col, ascending=True).tail(15),
                             x=col, y='state', orientation='h',
                             title=f'{get_column_label(col)} by State')
                break

    # Category/cost data
    elif 'cost_type' in df.columns:
        fig = px.bar(df, x='cost_type', y='amount_dollars',
                     title='Cost Comparison')

    # Nationality data
    elif 'nationality' in df.columns:
        fig = px.pie(df.head(10), values='count', names='nationality',
                     title='Deportations by Nationality')

    # Generic bar chart fallback
    if fig is None and len(df.columns) >= 2:
        numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
        numeric_cols = [c for c in numeric_cols if c not in HIDDEN_COLUMNS]
        if numeric_cols:
            cat_cols = df.select_dtypes(include=['object']).columns.tolist()
            if cat_cols:
                fig = px.bar(df.head(20), x=cat_cols[0], y=numeric_cols[0],
                             title=f'{get_column_label(numeric_cols[0])} by {get_column_label(cat_cols[0])}')

    if fig is None:
        return html.P("Unable to generate visualization for this dataset.", className='no-data'), {'display': 'block'}

    # Style the chart
    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor=COLORS['chart_bg'],
        plot_bgcolor=COLORS['chart_bg'],
        font=dict(family='Source Sans Pro', color=COLORS['text']),
        margin=dict(t=50, b=50),
        height=400
    )

    return html.Div([
        dcc.Graph(figure=fig, config={'displayModeBar': False}),
        html.Button("✕ Close Chart", id='close-viz-btn', className='btn-preset btn-preset-clear',
                    style={'marginTop': '10px'})
    ], style={'marginBottom': '20px'}), {'display': 'block'}


@callback(
    Output('data-table-container', 'children'),
    Output('current-data-store', 'data'),
    Input('table-selector', 'value'),
    Input('year-filter', 'value'),
    Input('search-filter', 'value'),
    Input('compare-selector', 'value'),
)
def update_data_table(table_name, year_filter, search_filter, compare_table):
    """Update the data table based on selections with formatted values."""
    if not table_name:
        return html.P("Select a dataset to explore."), None

    # Build query
    query = f'SELECT * FROM {table_name}'
    params = []
    year_col = 'fiscal_year' if table_name in ['deportations', 'deportations_by_nationality'] else 'year'

    if year_filter:
        query += f' WHERE {year_col} = ?'
        params.append(year_filter)

    data = query_data(query, params if params else None)

    if not data:
        return html.P("No data found for the selected criteria.", className='no-data'), None

    df = pd.DataFrame(data)

    # Apply search filter
    if search_filter:
        mask = df.astype(str).apply(lambda x: x.str.contains(search_filter, case=False, na=False)).any(axis=1)
        df = df[mask]

    if df.empty:
        return html.P("No data found matching your search.", className='no-data'), None

    # Store raw data for export
    raw_data = df.to_dict('records')

    # Remove hidden columns
    display_df = df.drop(columns=[c for c in HIDDEN_COLUMNS if c in df.columns], errors='ignore')

    # Format values for display
    for col in display_df.columns:
        if col in CURRENCY_COLUMNS or col in NUMBER_COLUMNS or col in PERCENTAGE_COLUMNS:
            display_df[col] = display_df[col].apply(lambda x: format_value(x, col))

    # Create columns with human-readable names
    columns = [{'name': get_column_label(col), 'id': col} for col in display_df.columns]

    table = dash_table.DataTable(
        data=display_df.to_dict('records'),
        columns=columns,
        page_size=15,
        sort_action='native',
        filter_action='native',
        style_table={'overflowX': 'auto'},
        style_header={
            'backgroundColor': COLORS['secondary'],
            'color': COLORS['text'],
            'fontWeight': 'bold',
            'fontFamily': 'Source Sans Pro'
        },
        style_cell={
            'backgroundColor': COLORS['primary'],
            'color': COLORS['text'],
            'fontFamily': 'Source Sans Pro',
            'padding': '12px',
            'textAlign': 'left',
            'border': f'1px solid {COLORS["grid"]}',
            'maxWidth': '300px',
            'overflow': 'hidden',
            'textOverflow': 'ellipsis'
        },
        style_data_conditional=[
            {'if': {'row_index': 'odd'}, 'backgroundColor': COLORS['secondary']}
        ],
        style_filter={
            'backgroundColor': COLORS['chart_bg'],
            'color': COLORS['text']
        },
        tooltip_data=[
            {col: {'value': str(row[col]), 'type': 'markdown'} for col in display_df.columns}
            for row in display_df.to_dict('records')
        ],
        tooltip_duration=None
    )

    # Handle comparison table
    if compare_table and compare_table != table_name:
        compare_data = query_data(f'SELECT * FROM {compare_table}')
        if compare_data:
            compare_df = pd.DataFrame(compare_data)
            compare_df = compare_df.drop(columns=[c for c in HIDDEN_COLUMNS if c in compare_df.columns], errors='ignore')

            for col in compare_df.columns:
                if col in CURRENCY_COLUMNS or col in NUMBER_COLUMNS or col in PERCENTAGE_COLUMNS:
                    compare_df[col] = compare_df[col].apply(lambda x: format_value(x, col))

            compare_columns = [{'name': get_column_label(col), 'id': col} for col in compare_df.columns]

            compare_table_component = dash_table.DataTable(
                data=compare_df.to_dict('records'),
                columns=compare_columns,
                page_size=10,
                sort_action='native',
                style_table={'overflowX': 'auto'},
                style_header={
                    'backgroundColor': COLORS['blue'],
                    'color': COLORS['text'],
                    'fontWeight': 'bold',
                    'fontFamily': 'Source Sans Pro'
                },
                style_cell={
                    'backgroundColor': COLORS['primary'],
                    'color': COLORS['text'],
                    'fontFamily': 'Source Sans Pro',
                    'padding': '10px',
                    'textAlign': 'left',
                    'border': f'1px solid {COLORS["grid"]}'
                },
                style_data_conditional=[
                    {'if': {'row_index': 'odd'}, 'backgroundColor': COLORS['secondary']}
                ]
            )

            return html.Div([
                html.H5("Primary Dataset", style={'color': COLORS['accent'], 'marginBottom': '10px'}),
                table,
                html.H5("Comparison Dataset", style={'color': COLORS['blue'], 'marginTop': '30px', 'marginBottom': '10px'}),
                compare_table_component
            ]), raw_data

    return table, raw_data


@callback(
    Output('download-csv', 'data'),
    Input('export-csv-btn', 'n_clicks'),
    State('table-selector', 'value'),
    State('current-data-store', 'data'),
    prevent_initial_call=True
)
def export_csv(n_clicks, table_name, stored_data):
    """Export current data to CSV."""
    if not n_clicks or not stored_data:
        return None

    df = pd.DataFrame(stored_data)
    # Remove hidden columns for export
    df = df.drop(columns=[c for c in HIDDEN_COLUMNS if c in df.columns], errors='ignore')
    # Rename columns
    df.columns = [get_column_label(c) for c in df.columns]

    filename = f'ice_data_{table_name}.csv'
    return dcc.send_data_frame(df.to_csv, filename, index=False)


@callback(
    Output('download-json', 'data'),
    Input('export-json-btn', 'n_clicks'),
    State('table-selector', 'value'),
    State('current-data-store', 'data'),
    prevent_initial_call=True
)
def export_json(n_clicks, table_name, stored_data):
    """Export current data to JSON."""
    if not n_clicks or not stored_data:
        return None

    # Remove hidden columns
    clean_data = []
    for row in stored_data:
        clean_row = {get_column_label(k): v for k, v in row.items() if k not in HIDDEN_COLUMNS}
        clean_data.append(clean_row)

    import json
    filename = f'ice_data_{table_name}.json'
    return dict(content=json.dumps(clean_data, indent=2), filename=filename)


@callback(
    Output('download-excel', 'data'),
    Input('export-excel-btn', 'n_clicks'),
    State('table-selector', 'value'),
    State('current-data-store', 'data'),
    prevent_initial_call=True
)
def export_excel(n_clicks, table_name, stored_data):
    """Export current data to Excel."""
    if not n_clicks or not stored_data:
        return None

    df = pd.DataFrame(stored_data)
    # Remove hidden columns
    df = df.drop(columns=[c for c in HIDDEN_COLUMNS if c in df.columns], errors='ignore')
    # Rename columns
    df.columns = [get_column_label(c) for c in df.columns]

    filename = f'ice_data_{table_name}.xlsx'
    return dcc.send_data_frame(df.to_excel, filename, index=False, engine='openpyxl')


@callback(
    Output('calculator-result', 'children'),
    Input('calc-income', 'value'),
    Input('calc-state', 'value'),
    Input('calc-status', 'value')
)
def update_calculator(income, state, status):
    """Calculate and display personal ICE cost contribution."""
    if not income or income <= 0:
        return html.Div([
            html.P("Enter your income to see your contribution", style={'color': COLORS['text_muted']})
        ])

    # Adjust for filing status
    if status == 'married':
        adjusted_income = income * 0.9  # Slightly lower effective rate
    elif status == 'hoh':
        adjusted_income = income * 0.95
    else:
        adjusted_income = income

    result = get_cost_calculator_context(adjusted_income, state)

    return html.Div([
        html.H2(f"${result['annual']:,.2f}", className='result-amount', id='result-value'),
        html.P("Your Annual Contribution to ICE Enforcement", className='result-label'),

        html.Div([
            html.Div([
                html.Div(f"${result['monthly']:,.2f}", className='comparison-value'),
                html.Div("Per Month", className='comparison-label')
            ], className='comparison-item'),
            html.Div([
                html.Div(f"${result['daily']:,.2f}", className='comparison-value'),
                html.Div("Per Day", className='comparison-label')
            ], className='comparison-item'),
            html.Div([
                html.Div(result['bracket'], className='comparison-value', style={'fontSize': '1rem'}),
                html.Div("Tax Bracket", className='comparison-label')
            ], className='comparison-item'),
        ], className='result-comparison'),

        html.P([
            "Your contribution could fund ", html.Strong(f"{result['comparisons']['detainee_days']} days"),
            " of detention, or provide ", html.Strong(f"{int(result['comparisons']['meals'])} school meals"),
            " for children."
        ], className='result-context', style={'marginTop': '25px'}),

        # Share button
        html.Div([
            html.Button(
                "Share This",
                id='share-calc-result',
                className='btn-export',
                style={'marginTop': '20px'}
            )
        ], style={'textAlign': 'center'})
    ])


# Clientside callback to trigger counter animation on page load
clientside_callback(
    """
    function(tab) {
        if (window.dash_clientside && window.dash_clientside.wow_features) {
            window.dash_clientside.wow_features.init();
        }
        return window.dash_clientside.no_update;
    }
    """,
    Output('tabs', 'className'),
    Input('tabs', 'active_tab')
)


# Callback for narratives sub-tabs
@callback(
    Output('narrative-content', 'children'),
    Input('narrative-tabs', 'active_tab')
)
def render_narrative_content(active_tab):
    """Render content for narrative sub-tabs."""
    if active_tab == 'narrative-criminality':
        return get_criminality_myth_content()
    elif active_tab == 'narrative-memorial':
        return get_memorial_content()
    elif active_tab == 'narrative-abuse':
        return get_abuse_archive_content()
    elif active_tab == 'narrative-globe':
        return get_deportation_globe_content()
    elif active_tab == 'narrative-heatmap':
        return get_arrest_heatmap_content()
    elif active_tab == 'narrative-cartogram':
        return get_detention_cartogram_content()
    elif active_tab == 'narrative-logistics':
        return get_logistics_map_content()
    elif active_tab == 'narrative-isotype':
        return get_isotype_timeline_content()
    elif active_tab == 'narrative-surveillance':
        return get_surveillance_tracker_content()
    elif active_tab == 'narrative-sankey':
        return get_economic_sankey_content()
    elif active_tab == 'narrative-profit':
        return get_profit_correlation_content()
    elif active_tab == 'narrative-bidding':
        return get_rigged_bidding_content()
    elif active_tab == 'narrative-hydra':
        return get_corporate_hydra_content()
    elif active_tab == 'narrative-media':
        return get_media_pulse_content()
    elif active_tab == 'narrative-gaps':
        return get_data_gaps_content()
    elif active_tab == 'narrative-bayesian':
        return get_bayesian_analysis_content()
    return html.Div("Select a narrative to explore.")


# Callback for criminality waffle chart reveal
clientside_callback(
    """
    function(n_clicks) {
        if (n_clicks) {
            const grid = document.getElementById('criminality-waffle-grid');
            const legend = document.getElementById('waffle-legend');
            const aftermath = document.getElementById('aftermath-container');
            const beforeReveal = document.getElementById('before-reveal');

            if (grid && legend && aftermath) {
                // Hide before reveal section
                if (beforeReveal) {
                    beforeReveal.style.display = 'none';
                }

                // Reveal cells with staggered animation
                const cells = grid.querySelectorAll('.waffle-cell');
                cells.forEach((cell, index) => {
                    setTimeout(() => {
                        cell.classList.add('revealed');
                    }, index * 3);
                });

                // Show legend after partial reveal
                setTimeout(() => {
                    legend.style.display = 'flex';
                }, 1000);

                // Show aftermath after full reveal
                setTimeout(() => {
                    aftermath.style.display = 'block';
                }, cells.length * 3 + 500);
            }
        }
        return window.dash_clientside.no_update;
    }
    """,
    Output('criminality-reveal-btn', 'disabled'),
    Input('criminality-reveal-btn', 'n_clicks'),
    prevent_initial_call=True
)


# Landing page: "Reveal the Truth" button - shows document section
clientside_callback(
    REVEAL_JS,
    Output('intro-overlay', 'className'),
    Input('begin-reveal-btn', 'n_clicks'),
    prevent_initial_call=True
)


# Landing page: "Lift All Redactions" button - reveals all hidden truths
clientside_callback(
    LIFT_ALL_JS,
    Output('gov-document', 'className'),
    Input('lift-redactions-btn', 'n_clicks'),
    prevent_initial_call=True
)


# Callback for taxpayer receipt generation
@callback(
    [Output('taxpayer-receipt-output', 'children'),
     Output('opportunity-cost-output', 'children')],
    Input('generate-receipt-btn', 'n_clicks'),
    [State('receipt-income', 'value'),
     State('receipt-status', 'value')],
    prevent_initial_call=True
)
def generate_receipt(n_clicks, income, status):
    """Generate taxpayer receipt when button is clicked."""
    if not income or income <= 0:
        return html.Div("Please enter a valid income"), []

    # Generate receipt HTML
    receipt = generate_receipt_html(income, status)

    # Calculate and generate opportunity costs
    calc = calculate_tax_contribution(income, status)
    opportunities = generate_opportunity_costs(calc['ice_contribution'])

    return receipt, opportunities


# ============================================
# SHARE FUNCTIONALITY CALLBACKS
# ============================================

# Clientside callback for Signal share (copies to clipboard and attempts to open Signal)
clientside_callback(
    """
    function(n_clicks) {
        if (n_clicks) {
            var shareText = "The Cost of Enforcement - ICE Data Explorer\\n\\n" +
                "Interactive investigation into U.S. immigration detention & deportation.\\n\\n" +
                "Key findings:\\n" +
                "• $170B enforcement budget (largest ever)\\n" +
                "• 73,000 currently detained (record high)\\n" +
                "• 73% have no criminal record\\n\\n" +
                "Explore the data: https://ice-data-explorer.onrender.com\\n\\n" +
                "Know Your Rights: https://www.aclu.org/know-your-rights/immigrants-rights";

            // Copy to clipboard
            if (navigator.clipboard && navigator.clipboard.writeText) {
                navigator.clipboard.writeText(shareText);
            }

            // Try to open Signal (works if app is installed)
            var signalUrl = 'signal://send?text=' + encodeURIComponent(shareText);
            window.open(signalUrl, '_blank');

            // Show feedback
            alert('Message copied. If Signal does not open automatically, paste the copied text into Signal manually.');
        }
        return window.dash_clientside.no_update;
    }
    """,
    Output('fixed-share-signal', 'n_clicks'),
    Input('fixed-share-signal', 'n_clicks'),
    prevent_initial_call=True
)


# Clientside callback for copy to clipboard
clientside_callback(
    """
    function(n_clicks) {
        if (n_clicks) {
            var shareText = "The Cost of Enforcement - ICE Data Explorer\\n\\n" +
                "Interactive investigation into U.S. immigration detention & deportation.\\n" +
                "https://ice-data-explorer.onrender.com";

            if (navigator.clipboard && navigator.clipboard.writeText) {
                navigator.clipboard.writeText(shareText).then(function() {
                    alert('Link copied to clipboard!');
                });
            } else {
                // Fallback
                var textarea = document.createElement('textarea');
                textarea.value = shareText;
                document.body.appendChild(textarea);
                textarea.select();
                document.execCommand('copy');
                document.body.removeChild(textarea);
                alert('Link copied to clipboard!');
            }
        }
        return window.dash_clientside.no_update;
    }
    """,
    Output('fixed-share-copy', 'n_clicks'),
    Input('fixed-share-copy', 'n_clicks'),
    prevent_initial_call=True
)


# Alert Widget: Share via Signal
clientside_callback(
    """
    function(n_clicks, message, alertType, location) {
        if (n_clicks && message) {
            var typeLabels = {
                'vehicle': 'ICE Vehicle Sighting',
                'enforcement': 'Enforcement Activity',
                'checkpoint': 'Checkpoint',
                'raid': 'Raid/Operation',
                'other': 'Other Activity'
            };

            var alertText = "COMMUNITY ALERT - " + (typeLabels[alertType] || 'ICE Activity') + "\\n\\n" +
                message + "\\n\\n" +
                "Location: " + (location || 'Not specified') + "\\n\\n" +
                "Stay safe. Know Your Rights: https://www.aclu.org/know-your-rights/immigrants-rights\\n" +
                "Report activity: https://unitedwedream.org/protect";

            // Copy to clipboard
            if (navigator.clipboard && navigator.clipboard.writeText) {
                navigator.clipboard.writeText(alertText);
            }

            // Try to open Signal
            var signalUrl = 'signal://send?text=' + encodeURIComponent(alertText);
            window.open(signalUrl, '_blank');

            alert('Alert copied! Paste into Signal to share with your community.');
        } else if (n_clicks && !message) {
            alert('Please enter a message to share.');
        }
        return window.dash_clientside.no_update;
    }
    """,
    Output('quick-signal-share', 'n_clicks'),
    Input('quick-signal-share', 'n_clicks'),
    [State('alert-message-input', 'value'),
     State('alert-type-select', 'value'),
     State('alert-location-input', 'value')],
    prevent_initial_call=True
)


# Alert Widget: Copy to clipboard
clientside_callback(
    """
    function(n_clicks, message, alertType, location) {
        if (n_clicks && message) {
            var typeLabels = {
                'vehicle': 'ICE Vehicle Sighting',
                'enforcement': 'Enforcement Activity',
                'checkpoint': 'Checkpoint',
                'raid': 'Raid/Operation',
                'other': 'Other Activity'
            };

            var alertText = "COMMUNITY ALERT - " + (typeLabels[alertType] || 'ICE Activity') + "\\n\\n" +
                message + "\\n\\n" +
                "Location: " + (location || 'Not specified') + "\\n\\n" +
                "Stay safe. Know Your Rights: https://www.aclu.org/know-your-rights/immigrants-rights";

            if (navigator.clipboard && navigator.clipboard.writeText) {
                navigator.clipboard.writeText(alertText).then(function() {
                    alert('Alert copied to clipboard!');
                });
            } else {
                var textarea = document.createElement('textarea');
                textarea.value = alertText;
                document.body.appendChild(textarea);
                textarea.select();
                document.execCommand('copy');
                document.body.removeChild(textarea);
                alert('Alert copied to clipboard!');
            }
        } else if (n_clicks && !message) {
            alert('Please enter a message to share.');
        }
        return window.dash_clientside.no_update;
    }
    """,
    Output('quick-copy-alert', 'n_clicks'),
    Input('quick-copy-alert', 'n_clicks'),
    [State('alert-message-input', 'value'),
     State('alert-type-select', 'value'),
     State('alert-location-input', 'value')],
    prevent_initial_call=True
)


if __name__ == '__main__':
    app.run(debug=True, port=8050)
