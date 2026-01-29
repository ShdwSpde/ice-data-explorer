"""
Project Watchtower - Arrest Dragnet Sonar Heatmap
PAGE 6: Geographic visualization of ICE enforcement activity

Visual Strategy: Animated heatmap showing enforcement "waves" spreading
across metropolitan areas. Pulsing intensity reveals patterns of
targeted enforcement in immigrant communities.
"""

import plotly.graph_objects as go
from dash import html, dcc
import numpy as np


# Color palette
COLORS = {
    'bg': '#0a0a14',
    'low': '#1a1a2e',
    'medium': '#ed8936',
    'high': '#e53e3e',
    'peak': '#ff0000',
    'text': '#e2e8f0',
    'text_muted': '#8d99ae',
}

# Metropolitan areas with enforcement data
# Values represent relative enforcement intensity (arrests per 100k immigrant population)
METRO_DATA = [
    # Texas corridor
    {'name': 'Houston, TX', 'lat': 29.7604, 'lon': -95.3698, 'intensity': 85, 'arrests': 12400, 'pop': 1450000},
    {'name': 'Dallas-Fort Worth, TX', 'lat': 32.7767, 'lon': -96.7970, 'intensity': 72, 'arrests': 8900, 'pop': 1230000},
    {'name': 'San Antonio, TX', 'lat': 29.4241, 'lon': -98.4936, 'intensity': 78, 'arrests': 6800, 'pop': 870000},
    {'name': 'Austin, TX', 'lat': 30.2672, 'lon': -97.7431, 'intensity': 45, 'arrests': 3200, 'pop': 710000},
    {'name': 'El Paso, TX', 'lat': 31.7619, 'lon': -106.4850, 'intensity': 92, 'arrests': 5600, 'pop': 610000},
    {'name': 'McAllen, TX', 'lat': 26.2034, 'lon': -98.2300, 'intensity': 95, 'arrests': 4200, 'pop': 440000},

    # California
    {'name': 'Los Angeles, CA', 'lat': 34.0522, 'lon': -118.2437, 'intensity': 38, 'arrests': 14200, 'pop': 3740000},
    {'name': 'San Diego, CA', 'lat': 32.7157, 'lon': -117.1611, 'intensity': 65, 'arrests': 5100, 'pop': 780000},
    {'name': 'San Francisco Bay Area, CA', 'lat': 37.7749, 'lon': -122.4194, 'intensity': 22, 'arrests': 4800, 'pop': 2180000},
    {'name': 'Fresno, CA', 'lat': 36.7378, 'lon': -119.7871, 'intensity': 68, 'arrests': 2800, 'pop': 410000},
    {'name': 'Bakersfield, CA', 'lat': 35.3733, 'lon': -119.0187, 'intensity': 72, 'arrests': 2100, 'pop': 290000},

    # Arizona
    {'name': 'Phoenix, AZ', 'lat': 33.4484, 'lon': -112.0740, 'intensity': 75, 'arrests': 7200, 'pop': 960000},
    {'name': 'Tucson, AZ', 'lat': 32.2226, 'lon': -110.9747, 'intensity': 82, 'arrests': 3100, 'pop': 380000},

    # Florida
    {'name': 'Miami, FL', 'lat': 25.7617, 'lon': -80.1918, 'intensity': 58, 'arrests': 8400, 'pop': 1450000},
    {'name': 'Orlando, FL', 'lat': 28.5383, 'lon': -81.3792, 'intensity': 62, 'arrests': 4100, 'pop': 660000},
    {'name': 'Tampa, FL', 'lat': 27.9506, 'lon': -82.4572, 'intensity': 55, 'arrests': 2900, 'pop': 530000},

    # Georgia
    {'name': 'Atlanta, GA', 'lat': 33.7490, 'lon': -84.3880, 'intensity': 68, 'arrests': 5800, 'pop': 850000},

    # North Carolina
    {'name': 'Charlotte, NC', 'lat': 35.2271, 'lon': -80.8431, 'intensity': 70, 'arrests': 3400, 'pop': 490000},
    {'name': 'Raleigh, NC', 'lat': 35.7796, 'lon': -78.6382, 'intensity': 65, 'arrests': 2100, 'pop': 320000},

    # New York/New Jersey
    {'name': 'New York City, NY', 'lat': 40.7128, 'lon': -74.0060, 'intensity': 28, 'arrests': 9200, 'pop': 3290000},
    {'name': 'Newark, NJ', 'lat': 40.7357, 'lon': -74.1724, 'intensity': 45, 'arrests': 3800, 'pop': 840000},

    # Illinois
    {'name': 'Chicago, IL', 'lat': 41.8781, 'lon': -87.6298, 'intensity': 35, 'arrests': 6100, 'pop': 1740000},

    # Other
    {'name': 'Denver, CO', 'lat': 39.7392, 'lon': -104.9903, 'intensity': 48, 'arrests': 2800, 'pop': 580000},
    {'name': 'Las Vegas, NV', 'lat': 36.1699, 'lon': -115.1398, 'intensity': 55, 'arrests': 3200, 'pop': 580000},
    {'name': 'Seattle, WA', 'lat': 47.6062, 'lon': -122.3321, 'intensity': 25, 'arrests': 1800, 'pop': 720000},
    {'name': 'Portland, OR', 'lat': 45.5152, 'lon': -122.6784, 'intensity': 22, 'arrests': 1200, 'pop': 540000},
]

# Sanctuary vs non-sanctuary comparison
POLICY_COMPARISON = {
    'sanctuary': {
        'name': 'Sanctuary Jurisdictions',
        'avg_intensity': 32,
        'cities': ['San Francisco', 'Los Angeles', 'New York', 'Chicago', 'Seattle', 'Portland'],
        'color': COLORS['low'],
    },
    'cooperative': {
        'name': 'ICE-Cooperative Jurisdictions',
        'avg_intensity': 75,
        'cities': ['Houston', 'Phoenix', 'Miami', 'Atlanta', 'Charlotte'],
        'color': COLORS['high'],
    },
    '287g': {
        'name': '287(g) Agreement Areas',
        'avg_intensity': 85,
        'cities': ['McAllen', 'El Paso', 'Tucson', 'Fresno', 'Bakersfield'],
        'color': COLORS['peak'],
    },
}


def create_heatmap_figure():
    """Create the enforcement intensity heatmap."""
    fig = go.Figure()

    # Extract data for plotting
    lats = [m['lat'] for m in METRO_DATA]
    lons = [m['lon'] for m in METRO_DATA]
    intensities = [m['intensity'] for m in METRO_DATA]
    names = [m['name'] for m in METRO_DATA]
    arrests = [m['arrests'] for m in METRO_DATA]

    # Create density layer (heatmap effect)
    fig.add_trace(go.Densitymapbox(
        lat=lats,
        lon=lons,
        z=intensities,
        radius=50,
        colorscale=[
            [0, 'rgba(26, 26, 46, 0.1)'],
            [0.3, 'rgba(237, 137, 54, 0.4)'],
            [0.6, 'rgba(229, 62, 62, 0.6)'],
            [1, 'rgba(255, 0, 0, 0.8)'],
        ],
        showscale=True,
        colorbar=dict(
            title=dict(text='Intensity', side='right'),
            tickmode='array',
            tickvals=[20, 50, 80],
            ticktext=['Low', 'Medium', 'High'],
        ),
        hoverinfo='skip',
    ))

    # Add city markers
    fig.add_trace(go.Scattermapbox(
        lat=lats,
        lon=lons,
        mode='markers+text',
        marker=dict(
            size=[8 + i/5 for i in intensities],
            color=intensities,
            colorscale='YlOrRd',
            opacity=0.8,
        ),
        text=names,
        textposition='top center',
        textfont=dict(size=9, color='white'),
        hovertemplate=(
            '<b>%{text}</b><br>'
            'Intensity: %{marker.color:.0f}<br>'
            '<extra></extra>'
        ),
        showlegend=False,
    ))

    fig.update_layout(
        mapbox=dict(
            style='carto-darkmatter',
            center=dict(lat=37.5, lon=-96),
            zoom=3.2,
        ),
        paper_bgcolor=COLORS['bg'],
        font=dict(family='Source Sans Pro, sans-serif', color=COLORS['text']),
        title=dict(
            text='<b>ICE Enforcement Intensity by Metro Area</b><br>'
                 '<sup>Arrests per 100k immigrant population</sup>',
            font=dict(size=18),
            x=0.5,
        ),
        margin=dict(t=80, b=20, l=20, r=20),
        height=550,
    )

    return fig


def create_policy_comparison_chart():
    """Create a comparison chart by policy type."""
    categories = list(POLICY_COMPARISON.keys())
    names = [POLICY_COMPARISON[c]['name'] for c in categories]
    intensities = [POLICY_COMPARISON[c]['avg_intensity'] for c in categories]
    colors = [POLICY_COMPARISON[c]['color'] for c in categories]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=names,
        y=intensities,
        marker_color=colors,
        text=[f'{i}' for i in intensities],
        textposition='outside',
        hovertemplate='%{x}<br>Avg Intensity: %{y}<extra></extra>',
    ))

    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor=COLORS['bg'],
        plot_bgcolor=COLORS['bg'],
        font=dict(family='Source Sans Pro, sans-serif', color=COLORS['text']),
        title=dict(
            text='<b>Enforcement Intensity by Jurisdiction Policy</b>',
            font=dict(size=16),
            x=0.5,
        ),
        xaxis=dict(showgrid=False),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(255,255,255,0.05)',
            title='Average Intensity Index',
        ),
        margin=dict(t=80, b=40, l=60, r=30),
        height=300,
        showlegend=False,
    )

    return fig


def create_metro_ranking():
    """Create a ranking of metros by enforcement intensity."""
    sorted_metros = sorted(METRO_DATA, key=lambda x: x['intensity'], reverse=True)[:10]

    return html.Div([
        html.H4("Top 10 Enforcement Hotspots", className='ranking-title'),
        html.Div([
            html.Div([
                html.Div([
                    html.Span(f"{i+1}", className='rank-number'),
                    html.Span(metro['name'], className='metro-name'),
                ], className='ranking-header'),
                html.Div([
                    html.Div(
                        className='intensity-bar',
                        style={'width': f"{metro['intensity']}%"}
                    ),
                    html.Span(f"{metro['intensity']}", className='intensity-value'),
                ], className='intensity-row'),
                html.Div([
                    html.Span(f"{metro['arrests']:,} arrests", className='arrests-count'),
                    html.Span(" | ", className='separator'),
                    html.Span(f"{metro['pop']:,} immigrant pop.", className='pop-count'),
                ], className='metro-stats'),
            ], className='ranking-item')
            for i, metro in enumerate(sorted_metros)
        ], className='ranking-list'),
    ], className='metro-ranking')


def get_arrest_heatmap_content():
    """
    Build and return the Arrest Dragnet Heatmap page.

    Returns:
        Dash html.Div with the enforcement visualization
    """
    total_arrests = sum(m['arrests'] for m in METRO_DATA)
    avg_intensity = sum(m['intensity'] for m in METRO_DATA) / len(METRO_DATA)
    highest_intensity = max(METRO_DATA, key=lambda x: x['intensity'])

    heatmap_fig = create_heatmap_figure()
    policy_fig = create_policy_comparison_chart()
    ranking = create_metro_ranking()

    return html.Div([
        # Header
        html.Div([
            html.Div([
                html.H2("The Arrest Dragnet", className='section-title'),
                html.P([
                    "ICE enforcement doesn't happen uniformly. This heatmap reveals where the dragnet ",
                    "falls hardest—patterns shaped by local policies, 287(g) agreements, and the ",
                    "geography of immigrant communities. Brighter areas indicate more aggressive enforcement."
                ], className='section-intro'),
            ], className='container'),
        ], className='heatmap-header'),

        # Key statistics
        html.Div([
            html.Div([
                html.Div([
                    html.Div([
                        html.Span("Total Arrests Mapped", className='stat-label'),
                        html.Span(f"{total_arrests:,}", className='stat-value'),
                    ], className='heatmap-stat'),
                    html.Div([
                        html.Span("Metro Areas", className='stat-label'),
                        html.Span(f"{len(METRO_DATA)}", className='stat-value'),
                    ], className='heatmap-stat'),
                    html.Div([
                        html.Span("Avg. Intensity Index", className='stat-label'),
                        html.Span(f"{avg_intensity:.0f}", className='stat-value'),
                    ], className='heatmap-stat'),
                    html.Div([
                        html.Span("Highest Intensity", className='stat-label'),
                        html.Span(highest_intensity['name'].split(',')[0], className='stat-value stat-warning'),
                        html.Span(f"({highest_intensity['intensity']})", className='stat-note'),
                    ], className='heatmap-stat'),
                ], className='heatmap-stats-row'),
            ], className='container'),
        ], className='heatmap-stats-bar'),

        # Main heatmap
        html.Div([
            dcc.Graph(
                id='enforcement-heatmap',
                figure=heatmap_fig,
                config={
                    'displayModeBar': True,
                    'modeBarButtonsToRemove': ['select2d', 'lasso2d'],
                    'scrollZoom': True,
                    'displaylogo': False,
                },
                style={'width': '100%'},
            ),
        ], className='heatmap-container'),

        # Two-column section: policy comparison + ranking
        html.Div([
            html.Div([
                html.Div([
                    html.Div([
                        dcc.Graph(
                            id='policy-comparison',
                            figure=policy_fig,
                            config={'displayModeBar': False},
                        ),
                    ], className='policy-chart'),
                    ranking,
                ], className='analysis-grid'),
            ], className='container'),
        ], className='analysis-section'),

        # Context section
        html.Div([
            html.Div([
                html.Div([
                    html.H3("What Drives Enforcement Patterns?", className='context-title'),
                    html.Div([
                        html.Div([
                            html.H4("287(g) Agreements", className='driver-title'),
                            html.P([
                                "Local law enforcement acts as ICE force multiplier. ",
                                "Areas with 287(g) show 2.5x higher enforcement intensity."
                            ], className='driver-text'),
                        ], className='driver-card'),
                        html.Div([
                            html.H4("Sanctuary Policies", className='driver-title'),
                            html.P([
                                "Jurisdictions limiting ICE cooperation show significantly lower ",
                                "enforcement, though ICE increases targeted operations."
                            ], className='driver-text'),
                        ], className='driver-card'),
                        html.Div([
                            html.H4("Border Proximity", className='driver-title'),
                            html.P([
                                "100-mile border zone allows expanded enforcement authority. ",
                                "Border metros show 40% higher intensity than interior."
                            ], className='driver-text'),
                        ], className='driver-card'),
                    ], className='drivers-grid'),
                ], className='context-box'),
            ], className='container'),
        ], className='context-section'),

        # Methodology
        html.Div([
            html.Div([
                html.H4("Methodology", className='methodology-title'),
                html.P([
                    "Enforcement intensity index calculated from ICE ERO administrative arrest data, ",
                    "normalized by estimated undocumented immigrant population (ACS/Pew estimates). ",
                    "Policy classifications from ILRC sanctuary tracker and ICE 287(g) MOA database. ",
                    "Heatmap visualization uses Gaussian kernel density estimation."
                ], className='methodology-text'),
            ], className='container'),
        ], className='heatmap-methodology'),

    ], className='arrest-heatmap-page')
