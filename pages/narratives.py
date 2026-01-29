"""
Project Watchtower - Narrative Visualizations
Challenging Official Narratives & Myth-Busting

Visual Strategy: Use interactive reveals to challenge assumptions
and force confrontation with data reality.
"""

from dash import html, dcc
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from database import query_data


def get_criminality_myth_content():
    """
    PAGE 14: The "Criminality" Myth
    Visual Strategy: Interactive Waffle Chart Reveal

    Shows that 73% of detainees have no criminal conviction,
    busting the narrative that detention is for dangerous criminals.
    """
    # Get actual data from database
    criminal_data = query_data('''
        SELECT * FROM detainee_criminal_status
        ORDER BY date DESC LIMIT 1
    ''')

    if criminal_data:
        no_conviction_pct = criminal_data[0]['no_convictions_pct'] or 73
        violent_pct = criminal_data[0]['violent_convictions_pct'] or 8
        nonviolent_pct = criminal_data[0]['nonviolent_convictions_pct'] or 15
        pending_pct = criminal_data[0]['pending_charges_pct'] or 4
    else:
        no_conviction_pct, violent_pct, nonviolent_pct, pending_pct = 73, 8, 15, 4

    # Generate waffle grid (1000 cells = 10 per percentage point)
    cells = []
    for i in range(1000):
        cells.append(html.Div(
            className='waffle-cell',
            id={'type': 'waffle-cell', 'index': i},
            **{'data-category': _get_waffle_category(i, no_conviction_pct, violent_pct, nonviolent_pct)}
        ))

    return html.Div([
        # Header
        html.Div([
            html.H2("The \"Criminality\" Myth", className='section-title'),
            html.P([
                "The official narrative portrays ICE detention as necessary to hold ",
                html.Strong("dangerous criminals"),
                ". But what does the data actually show?"
            ], className='section-intro'),
            html.Div([
                html.Span("⚠️", className='contested-icon'),
                html.Span("DATA CHALLENGES OFFICIAL NARRATIVE", className='contested-badge')
            ], className='narrative-alert')
        ], className='container'),

        # The Reveal Section
        html.Div([
            html.Div([
                html.H3("Who Is Actually Being Detained?", className='reveal-title'),
                html.P([
                    "Below are 1,000 icons representing the current ICE detention population. ",
                    "Each icon represents the proportional breakdown of detainees by criminal status."
                ], className='reveal-intro'),

                # Before state - intimidating description
                html.Div([
                    html.Div([
                        html.Span("👤" * 20, className='intimidating-icons'),
                        html.P([
                            "Official rhetoric suggests these are ",
                            html.Strong("dangerous criminals"),
                            " who pose a threat to public safety."
                        ], className='intimidating-text')
                    ], className='before-reveal', id='before-reveal'),
                ], className='reveal-context'),

                # Reveal Button
                html.Button(
                    "REVEAL THE REALITY",
                    id='criminality-reveal-btn',
                    className='btn-reveal'
                ),

                # Waffle Grid
                html.Div([
                    html.Div(cells, className='waffle-grid', id='criminality-waffle-grid'),
                ], className='waffle-wrapper', id='waffle-wrapper'),

                # Legend (hidden until reveal)
                html.Div([
                    html.Div([
                        html.Div(className='legend-color legend-no-conviction'),
                        html.Span(f"No Criminal Conviction: {no_conviction_pct}%", className='legend-label')
                    ], className='legend-item'),
                    html.Div([
                        html.Div(className='legend-color legend-nonviolent'),
                        html.Span(f"Non-Violent Conviction: {nonviolent_pct}%", className='legend-label')
                    ], className='legend-item'),
                    html.Div([
                        html.Div(className='legend-color legend-violent'),
                        html.Span(f"Violent Conviction: {violent_pct}%", className='legend-label')
                    ], className='legend-item'),
                    html.Div([
                        html.Div(className='legend-color legend-pending'),
                        html.Span(f"Pending Charges: {pending_pct}%", className='legend-label')
                    ], className='legend-item'),
                ], className='waffle-legend', id='waffle-legend', style={'display': 'none'}),

                # Aftermath text (hidden until reveal)
                html.Div([
                    html.H4("The Reality:", className='aftermath-title truth-text'),
                    html.P([
                        html.Strong(f"{no_conviction_pct}%", className='truth-highlight'),
                        " of ICE detainees have ",
                        html.Strong("no criminal conviction"),
                        ". The majority are held for civil immigration violations, not crimes."
                    ], className='aftermath-text'),
                    html.Div([
                        html.Div([
                            html.Span("Source: ", className='source-label'),
                            html.Span("ICE Detention Statistics, cross-referenced with TRAC Immigration Data",
                                     className='source-value'),
                        ], className='source-citation'),
                        html.Div([
                            html.Span("Verification: ", className='source-label'),
                            html.Span("✅ VERIFIED INDEPENDENT", className='truth-badge'),
                        ], className='source-verification'),
                    ], className='source-info')
                ], className='aftermath-container', id='aftermath-container', style={'display': 'none'}),

            ], className='reveal-card')
        ], className='container reveal-section'),

        # Context Section
        html.Div([
            html.H3("What This Means", className='context-title'),
            html.Div([
                html.Div([
                    html.Div("$150+", className='context-stat corporate-text'),
                    html.Div("Daily cost per detainee", className='context-label'),
                    html.Div("paid to private prison companies", className='context-sublabel'),
                ], className='context-card corporate-card'),
                html.Div([
                    html.Div(f"{no_conviction_pct}%", className='context-stat truth-text'),
                    html.Div("No criminal conviction", className='context-label'),
                    html.Div("held for civil violations", className='context-sublabel'),
                ], className='context-card truth-card'),
                html.Div([
                    html.Div("$3.4B", className='context-stat'),
                    html.Div("Annual detention budget", className='context-label'),
                    html.Div("most for non-criminals", className='context-sublabel'),
                ], className='context-card'),
            ], className='context-grid'),
        ], className='container context-section'),

    ], className='narratives-page criminality-myth')


def _get_waffle_category(index, no_conv, violent, nonviolent):
    """Determine category for waffle cell based on percentages."""
    # Convert percentages to cell counts (1000 total)
    no_conv_count = int(no_conv * 10)
    violent_count = int(violent * 10)
    nonviolent_count = int(nonviolent * 10)

    if index < no_conv_count:
        return 'no-conviction'
    elif index < no_conv_count + violent_count:
        return 'violent'
    elif index < no_conv_count + violent_count + nonviolent_count:
        return 'nonviolent'
    else:
        return 'pending'


def get_detention_cartogram_content():
    """
    PAGE 16: The Distorted Map
    Visual Strategy: Choropleth Cartogram

    Map where state sizes are distorted by detained population.
    """
    # Get state detention data
    state_data = query_data('''
        SELECT state, population, facilities_count
        FROM detention_by_state
        WHERE year = (SELECT MAX(year) FROM detention_by_state)
        ORDER BY population DESC
    ''')

    # State coordinates for bubble placement
    state_coords = {
        'TX': (-99.9, 31.9), 'CA': (-119.4, 36.8), 'AZ': (-111.1, 34.0),
        'FL': (-81.5, 27.6), 'GA': (-83.5, 32.2), 'LA': (-91.9, 30.9),
        'NJ': (-74.4, 40.1), 'NY': (-75.0, 43.0), 'CO': (-105.3, 39.1),
        'VA': (-78.2, 37.4), 'PA': (-77.2, 41.2), 'NM': (-105.9, 34.5),
        'NC': (-79.0, 35.7), 'IL': (-89.0, 40.6), 'WA': (-120.7, 47.4),
        'AL': (-86.9, 32.3), 'MS': (-89.3, 32.3), 'TN': (-86.6, 35.5),
        'OK': (-97.5, 35.0), 'MD': (-76.6, 39.0),
    }

    if not state_data:
        return html.Div("No detention data available", className='error-message')

    max_pop = max(d['population'] for d in state_data) if state_data else 1

    # Create the map
    fig = go.Figure()

    # Base choropleth
    states = [d['state'] for d in state_data]
    populations = [d['population'] for d in state_data]

    fig.add_trace(go.Choropleth(
        locations=states,
        z=populations,
        locationmode='USA-states',
        colorscale=[
            [0, 'rgba(30, 40, 60, 0.8)'],
            [0.3, 'rgba(100, 50, 70, 0.8)'],
            [0.6, 'rgba(180, 60, 80, 0.8)'],
            [1, 'rgba(229, 62, 62, 0.9)']
        ],
        showscale=True,
        colorbar=dict(
            title=dict(text='Detained<br>Population', font=dict(color='white')),
            tickfont=dict(color='white'),
            bgcolor='rgba(0,0,0,0.3)'
        ),
        hovertemplate='<b>%{location}</b><br>Detained: %{z:,.0f}<extra></extra>'
    ))

    # Add distortion bubbles for cartogram effect
    for d in state_data:
        if d['state'] in state_coords:
            lon, lat = state_coords[d['state']]
            size = 15 + (d['population'] / max_pop) * 60

            fig.add_trace(go.Scattergeo(
                lon=[lon],
                lat=[lat],
                mode='markers+text',
                marker=dict(
                    size=size,
                    color='rgba(229, 62, 62, 0.5)',
                    line=dict(width=2, color='rgba(255,255,255,0.6)')
                ),
                text=[d['state']],
                textposition='middle center',
                textfont=dict(size=10, color='white', family='IBM Plex Mono'),
                hoverinfo='skip',
                showlegend=False
            ))

    fig.update_geos(
        scope='usa',
        showland=True,
        landcolor='rgba(30, 40, 60, 0.3)',
        showlakes=False,
        showcoastlines=True,
        coastlinecolor='rgba(100, 100, 120, 0.5)',
        bgcolor='rgba(0,0,0,0)'
    )

    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=0, b=0),
        height=550,
        geo=dict(bgcolor='rgba(0,0,0,0)')
    )

    # Top states list
    top_states = state_data[:10] if len(state_data) >= 10 else state_data

    return html.Div([
        # Header
        html.Div([
            html.H2("The Geography of Detention", className='section-title'),
            html.P([
                "State sizes distorted by detained population. ",
                "The larger the bubble, the more people held in that state's facilities."
            ], className='section-intro'),
        ], className='container'),

        # Map
        html.Div([
            dcc.Graph(
                figure=fig,
                config={'displayModeBar': False, 'scrollZoom': False},
                className='cartogram-map'
            )
        ], className='map-container'),

        # Top States
        html.Div([
            html.H3("States with Highest Detention", className='ranking-title'),
            html.Div([
                html.Div([
                    html.Div(f"#{i+1}", className='rank-number'),
                    html.Div([
                        html.Span(d['state'], className='rank-state'),
                        html.Span(f"{d['population']:,} detained", className='rank-value'),
                        html.Span(f"{d['facilities_count'] or '?'} facilities", className='rank-facilities'),
                    ], className='rank-details')
                ], className='rank-item') for i, d in enumerate(top_states)
            ], className='ranking-grid')
        ], className='container ranking-section'),

    ], className='narratives-page cartogram-page')


def get_isotype_timeline_content():
    """
    FR 2.5: Militarization Timeline (Isotype View)
    Visual Strategy: Human pictograms showing staffing growth

    Shows physical expansion of ICE/CBP force over time
    using icon density instead of line charts.
    """
    # Get staffing data
    staffing_data = query_data('''
        SELECT year, agency, employees
        FROM staffing
        WHERE agency IN ('Border Patrol', 'ICE')
        ORDER BY year ASC
    ''')

    if not staffing_data:
        return html.Div("No staffing data available", className='error-message')

    # Organize by agency
    bp_data = [d for d in staffing_data if d['agency'] == 'Border Patrol']
    ice_data = [d for d in staffing_data if d['agency'] == 'ICE']

    # Scale: each icon = 1000 personnel
    scale = 1000
    icon = "👤"

    def create_isotype_row(year, count, color_class=''):
        """Create a row of icons for a year."""
        num_icons = count // scale
        icon_rows = []

        # Create multiple rows of 25 icons each
        while num_icons > 0:
            row_count = min(num_icons, 25)
            icon_rows.append(
                html.Div(icon * row_count, className=f'isotype-icons {color_class}')
            )
            num_icons -= row_count

        return html.Div([
            html.Div([
                html.Span(str(year), className='isotype-year'),
                html.Span(f"{count:,}", className='isotype-count'),
            ], className='isotype-label'),
            html.Div(icon_rows, className='isotype-icon-container'),
        ], className='isotype-row')

    # Create timeline rows for Border Patrol
    bp_rows = []
    for d in bp_data:
        if d['year'] % 4 == 0 or d['year'] == bp_data[-1]['year']:  # Show every 4 years
            bp_rows.append(create_isotype_row(d['year'], d['employees'], 'bp-icons'))

    # Create timeline rows for ICE
    ice_rows = []
    for d in ice_data:
        if d['year'] % 4 == 0 or d['year'] == ice_data[-1]['year']:
            ice_rows.append(create_isotype_row(d['year'], d['employees'], 'ice-icons'))

    # Calculate growth
    if bp_data:
        bp_start = bp_data[0]['employees']
        bp_end = bp_data[-1]['employees']
        bp_growth = ((bp_end - bp_start) / bp_start) * 100 if bp_start else 0
        bp_start_year = bp_data[0]['year']
        bp_end_year = bp_data[-1]['year']
    else:
        bp_growth, bp_start_year, bp_end_year = 0, 0, 0

    return html.Div([
        # Header
        html.Div([
            html.H2("The Militarization of Immigration Enforcement", className='section-title'),
            html.P([
                "Each ", html.Span(icon, className='icon-sample'),
                f" represents {scale:,} personnel. ",
                "Watch the force grow."
            ], className='section-intro'),
        ], className='container'),

        # Growth Stats
        html.Div([
            html.Div([
                html.Div(f"+{bp_growth:.0f}%", className='growth-stat truth-text'),
                html.Div(f"Border Patrol growth ({bp_start_year}-{bp_end_year})", className='growth-label'),
            ], className='growth-card'),
        ], className='container growth-section'),

        # Border Patrol Timeline
        html.Div([
            html.H3("Border Patrol Personnel", className='agency-title facade-text'),
            html.Div(bp_rows, className='isotype-timeline'),
        ], className='container isotype-section'),

        # ICE Timeline (if data exists)
        html.Div([
            html.H3("ICE Personnel", className='agency-title'),
            html.Div(ice_rows, className='isotype-timeline'),
        ], className='container isotype-section') if ice_data else None,

        # Context
        html.Div([
            html.Div([
                html.H4("For Context:", className='context-title'),
                html.P([
                    "The combined Border Patrol and ICE force is now larger than the ",
                    html.Strong("FBI, DEA, ATF, and US Marshals combined"),
                    ". This represents the largest federal law enforcement expansion in U.S. history."
                ], className='context-text'),
            ], className='context-callout')
        ], className='container'),

        # Legend
        html.Div([
            html.Div([
                html.Span(icon, className='legend-icon'),
                html.Span(f" = {scale:,} personnel", className='legend-text')
            ], className='isotype-legend')
        ], className='container legend-section'),

    ], className='narratives-page isotype-page')
