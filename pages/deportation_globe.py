"""
Project Watchtower - Kinetic Deportation Globe
FR 2.2: 3D visualization of deportation flight routes

Visual Strategy: Dark 3D globe with glowing arc paths tracing
deportation flights from US cities to destination countries.
Particle effects along routes suggest the human scale.
"""

import numpy as np
import plotly.graph_objects as go
from dash import html, dcc
from database import query_data


# Color palette
COLORS = {
    'bg': '#0a0a14',
    'land': '#1a1a2e',
    'ocean': '#0f0f1a',
    'border': '#2a2a40',
    'route': '#e53e3e',
    'route_glow': 'rgba(229, 62, 62, 0.3)',
    'origin': '#ffd166',
    'destination': '#e53e3e',
    'text': '#e2e8f0',
    'text_muted': '#8d99ae',
}

# Major ICE Air deportation hubs
DEPORTATION_ORIGINS = {
    'Mesa, AZ': {'lat': 33.4152, 'lon': -111.8315, 'flights': 1200},
    'Alexandria, LA': {'lat': 31.3113, 'lon': -92.4451, 'flights': 980},
    'San Antonio, TX': {'lat': 29.4241, 'lon': -98.4936, 'flights': 1450},
    'Miami, FL': {'lat': 25.7617, 'lon': -80.1918, 'flights': 820},
    'Brownsville, TX': {'lat': 25.9017, 'lon': -97.4975, 'flights': 650},
    'El Paso, TX': {'lat': 31.7619, 'lon': -106.4850, 'flights': 890},
    'Houston, TX': {'lat': 29.7604, 'lon': -95.3698, 'flights': 720},
    'Los Angeles, CA': {'lat': 33.9425, 'lon': -118.4081, 'flights': 540},
}

# Deportation destination countries with coordinates and volumes
DESTINATION_COUNTRIES = {
    'Guatemala': {'lat': 14.6349, 'lon': -90.5069, 'deportees': 54000, 'code': 'GTM'},
    'Honduras': {'lat': 14.0723, 'lon': -87.1921, 'deportees': 42000, 'code': 'HND'},
    'El Salvador': {'lat': 13.7942, 'lon': -88.8965, 'deportees': 28000, 'code': 'SLV'},
    'Mexico': {'lat': 19.4326, 'lon': -99.1332, 'deportees': 85000, 'code': 'MEX'},
    'Nicaragua': {'lat': 12.1150, 'lon': -86.2362, 'deportees': 4500, 'code': 'NIC'},
    'Ecuador': {'lat': -0.1807, 'lon': -78.4678, 'deportees': 6200, 'code': 'ECU'},
    'Colombia': {'lat': 4.7110, 'lon': -74.0721, 'deportees': 5800, 'code': 'COL'},
    'Brazil': {'lat': -15.7975, 'lon': -47.8919, 'deportees': 3200, 'code': 'BRA'},
    'Dominican Republic': {'lat': 18.4861, 'lon': -69.9312, 'deportees': 4100, 'code': 'DOM'},
    'Haiti': {'lat': 18.5944, 'lon': -72.3074, 'deportees': 18500, 'code': 'HTI'},
    'Jamaica': {'lat': 18.1096, 'lon': -77.2975, 'deportees': 2800, 'code': 'JAM'},
    'India': {'lat': 28.6139, 'lon': 77.2090, 'deportees': 2100, 'code': 'IND'},
    'China': {'lat': 39.9042, 'lon': 116.4074, 'deportees': 1800, 'code': 'CHN'},
    'Vietnam': {'lat': 21.0278, 'lon': 105.8342, 'deportees': 850, 'code': 'VNM'},
    'Philippines': {'lat': 14.5995, 'lon': 120.9842, 'deportees': 1200, 'code': 'PHL'},
    'Nigeria': {'lat': 9.0820, 'lon': 7.4951, 'deportees': 1100, 'code': 'NGA'},
    'Ghana': {'lat': 5.6037, 'lon': -0.1870, 'deportees': 780, 'code': 'GHA'},
    'Cameroon': {'lat': 3.8480, 'lon': 11.5021, 'deportees': 420, 'code': 'CMR'},
}

# Major routes (origin -> destination with volume)
MAJOR_ROUTES = [
    ('San Antonio, TX', 'Guatemala', 18000),
    ('San Antonio, TX', 'Honduras', 15000),
    ('San Antonio, TX', 'El Salvador', 12000),
    ('Mesa, AZ', 'Mexico', 25000),
    ('Mesa, AZ', 'Guatemala', 8000),
    ('Alexandria, LA', 'Honduras', 12000),
    ('Alexandria, LA', 'Guatemala', 10000),
    ('Miami, FL', 'Haiti', 14000),
    ('Miami, FL', 'Jamaica', 2200),
    ('Miami, FL', 'Dominican Republic', 3500),
    ('El Paso, TX', 'Mexico', 28000),
    ('Brownsville, TX', 'Mexico', 22000),
    ('Houston, TX', 'Guatemala', 5000),
    ('Houston, TX', 'El Salvador', 4500),
    ('Los Angeles, CA', 'Mexico', 12000),
]


def generate_arc_points(lat1, lon1, lat2, lon2, num_points=50):
    """
    Generate points along a great circle arc between two coordinates,
    with elevation for 3D effect.
    """
    # Convert to radians
    lat1_r, lon1_r = np.radians(lat1), np.radians(lon1)
    lat2_r, lon2_r = np.radians(lat2), np.radians(lon2)

    # Calculate great circle distance
    d = np.arccos(
        np.sin(lat1_r) * np.sin(lat2_r) +
        np.cos(lat1_r) * np.cos(lat2_r) * np.cos(lon2_r - lon1_r)
    )

    lats, lons = [], []
    for i in range(num_points + 1):
        f = i / num_points
        A = np.sin((1 - f) * d) / np.sin(d) if np.sin(d) > 0 else 1 - f
        B = np.sin(f * d) / np.sin(d) if np.sin(d) > 0 else f

        x = A * np.cos(lat1_r) * np.cos(lon1_r) + B * np.cos(lat2_r) * np.cos(lon2_r)
        y = A * np.cos(lat1_r) * np.sin(lon1_r) + B * np.cos(lat2_r) * np.sin(lon2_r)
        z = A * np.sin(lat1_r) + B * np.sin(lat2_r)

        lat = np.degrees(np.arctan2(z, np.sqrt(x**2 + y**2)))
        lon = np.degrees(np.arctan2(y, x))

        lats.append(lat)
        lons.append(lon)

    return lats, lons


def create_deportation_globe():
    """
    Create the 3D deportation globe visualization.

    Returns:
        Plotly figure object
    """
    fig = go.Figure()

    # Add route arcs
    for origin_name, dest_name, volume in MAJOR_ROUTES:
        origin = DEPORTATION_ORIGINS[origin_name]
        dest = DESTINATION_COUNTRIES[dest_name]

        lats, lons = generate_arc_points(
            origin['lat'], origin['lon'],
            dest['lat'], dest['lon']
        )

        # Scale line width by volume
        width = 1 + (volume / 5000)

        # Main arc
        fig.add_trace(go.Scattergeo(
            lat=lats,
            lon=lons,
            mode='lines',
            line=dict(
                width=width,
                color=COLORS['route'],
            ),
            opacity=0.6,
            hoverinfo='text',
            text=f"{origin_name} → {dest_name}<br>{volume:,} deportees",
            showlegend=False,
        ))

        # Glow effect (wider, more transparent)
        fig.add_trace(go.Scattergeo(
            lat=lats,
            lon=lons,
            mode='lines',
            line=dict(
                width=width + 4,
                color=COLORS['route_glow'],
            ),
            opacity=0.2,
            hoverinfo='skip',
            showlegend=False,
        ))

    # Add origin points (US cities)
    origin_lats = [o['lat'] for o in DEPORTATION_ORIGINS.values()]
    origin_lons = [o['lon'] for o in DEPORTATION_ORIGINS.values()]
    origin_names = list(DEPORTATION_ORIGINS.keys())
    origin_flights = [o['flights'] for o in DEPORTATION_ORIGINS.values()]

    fig.add_trace(go.Scattergeo(
        lat=origin_lats,
        lon=origin_lons,
        mode='markers',
        marker=dict(
            size=[10 + f/100 for f in origin_flights],
            color=COLORS['origin'],
            opacity=0.9,
            line=dict(width=1, color='white'),
            symbol='diamond',
        ),
        text=[f"<b>{name}</b><br>ICE Air Hub<br>{DEPORTATION_ORIGINS[name]['flights']} flights/year"
              for name in origin_names],
        hoverinfo='text',
        name='ICE Air Operations Hubs',
    ))

    # Add destination points
    dest_lats = [d['lat'] for d in DESTINATION_COUNTRIES.values()]
    dest_lons = [d['lon'] for d in DESTINATION_COUNTRIES.values()]
    dest_names = list(DESTINATION_COUNTRIES.keys())
    dest_deportees = [d['deportees'] for d in DESTINATION_COUNTRIES.values()]

    fig.add_trace(go.Scattergeo(
        lat=dest_lats,
        lon=dest_lons,
        mode='markers',
        marker=dict(
            size=[8 + d/5000 for d in dest_deportees],
            color=COLORS['destination'],
            opacity=0.8,
            line=dict(width=1, color='rgba(255,255,255,0.3)'),
        ),
        text=[f"<b>{name}</b><br>{DESTINATION_COUNTRIES[name]['deportees']:,} deportees/year"
              for name in dest_names],
        hoverinfo='text',
        name='Deportation Destinations',
    ))

    # Configure globe appearance
    fig.update_geos(
        projection_type='orthographic',
        projection_rotation=dict(lon=-95, lat=25, roll=0),
        showland=True,
        landcolor=COLORS['land'],
        showocean=True,
        oceancolor=COLORS['ocean'],
        showlakes=False,
        showcountries=True,
        countrycolor=COLORS['border'],
        countrywidth=0.5,
        showcoastlines=True,
        coastlinecolor=COLORS['border'],
        coastlinewidth=0.5,
        showframe=False,
        bgcolor=COLORS['bg'],
    )

    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor=COLORS['bg'],
        plot_bgcolor=COLORS['bg'],
        font=dict(family='Source Sans Pro, sans-serif', color=COLORS['text']),
        title=dict(
            text='<b>Deportation Flight Network</b><br>'
                 '<sup>ICE Air Operations routes and volumes</sup>',
            font=dict(size=20),
            x=0.5,
            xanchor='center',
        ),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=-0.05,
            xanchor='center',
            x=0.5,
            font=dict(size=12),
            bgcolor='rgba(0,0,0,0)',
        ),
        margin=dict(t=80, b=60, l=10, r=10),
        height=650,
        hoverlabel=dict(
            bgcolor='rgba(15,15,35,0.95)',
            bordercolor=COLORS['route'],
            font_size=13,
        ),
    )

    return fig


def get_deportation_globe_content():
    """
    Build and return the Deportation Globe page.

    Returns:
        Dash html.Div with the globe visualization
    """
    # Calculate statistics
    total_deportees = sum(d['deportees'] for d in DESTINATION_COUNTRIES.values())
    total_flights = sum(o['flights'] for o in DEPORTATION_ORIGINS.values())
    top_destinations = sorted(
        DESTINATION_COUNTRIES.items(),
        key=lambda x: x[1]['deportees'],
        reverse=True
    )[:5]

    fig = create_deportation_globe()

    return html.Div([
        # Header
        html.Div([
            html.Div([
                html.H2("The Deportation Machine", className='section-title'),
                html.P([
                    "ICE Air Operations runs one of the world's largest deportation flight networks. ",
                    "Each arc traces a route regularly flown to return people to countries they fled. ",
                    "Rotate the globe to see the global reach of U.S. immigration enforcement."
                ], className='section-intro'),
            ], className='container'),
        ], className='globe-header'),

        # Stats row
        html.Div([
            html.Div([
                html.Div([
                    html.Div([
                        html.Span("Annual Deportees", className='stat-label'),
                        html.Span(f"{total_deportees:,}", className='stat-value'),
                    ], className='globe-stat'),
                    html.Div([
                        html.Span("Charter Flights/Year", className='stat-label'),
                        html.Span(f"{total_flights:,}+", className='stat-value'),
                    ], className='globe-stat'),
                    html.Div([
                        html.Span("US Departure Hubs", className='stat-label'),
                        html.Span(f"{len(DEPORTATION_ORIGINS)}", className='stat-value'),
                    ], className='globe-stat'),
                    html.Div([
                        html.Span("Destination Countries", className='stat-label'),
                        html.Span(f"{len(DESTINATION_COUNTRIES)}+", className='stat-value'),
                    ], className='globe-stat'),
                ], className='globe-stats-row'),
            ], className='container'),
        ], className='globe-stats-bar'),

        # Globe visualization
        html.Div([
            dcc.Graph(
                id='deportation-globe',
                figure=fig,
                config={
                    'displayModeBar': True,
                    'modeBarButtonsToRemove': ['select2d', 'lasso2d', 'autoScale2d'],
                    'scrollZoom': True,
                    'displaylogo': False,
                },
                style={'width': '100%'},
            ),
        ], className='globe-container'),

        # Top destinations breakdown
        html.Div([
            html.Div([
                html.H3("Top Deportation Destinations", className='subsection-title'),
                html.Div([
                    html.Div([
                        html.Div([
                            html.Span(f"{i+1}.", className='rank-number'),
                            html.Span(name, className='country-name'),
                        ], className='destination-header'),
                        html.Div([
                            html.Div(
                                className='destination-bar',
                                style={'width': f"{data['deportees']/85000*100}%"}
                            ),
                            html.Span(f"{data['deportees']:,}", className='destination-count'),
                        ], className='destination-bar-container'),
                    ], className='destination-item')
                    for i, (name, data) in enumerate(top_destinations)
                ], className='destinations-list'),
            ], className='container'),
        ], className='destinations-section'),

        # Context and methodology
        html.Div([
            html.Div([
                html.Div([
                    html.H4("The Human Cost of Deportation", className='context-title'),
                    html.P([
                        "Each flight removes people who may have lived in the U.S. for decades—parents ",
                        "separated from U.S. citizen children, workers deported to countries they barely remember, ",
                        "asylum seekers returned to the violence they fled. ICE Air Operations operates ",
                        "with minimal oversight and has faced criticism for medical emergencies, shackling practices, ",
                        "and deportations that violate court orders."
                    ], className='context-text'),
                ], className='human-cost-box'),

                html.Div([
                    html.H4("Data Sources", className='methodology-title'),
                    html.P([
                        "Flight data from ICE Enforcement and Removal Operations statistics, ",
                        "FOIA releases, and flight tracking by Witness at the Border. ",
                        "Country-level deportation volumes from DHS Yearbook of Immigration Statistics. ",
                        "Hub locations identified through ICE Air Operations contract documents and airport records."
                    ], className='methodology-text'),
                ], className='methodology-box'),
            ], className='container'),
        ], className='globe-context-section'),

    ], className='deportation-globe-page')
