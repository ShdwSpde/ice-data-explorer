"""
Project Watchtower - Surveillance Tech Stack Tracker
PAGE 12: The Layer Cake Reveal

Visual Strategy: 3D stacked visualization showing layers of surveillance data
stacking up to crush a generic citizen icon, highlighting the role of
non-prison tech contractors like Palantir, LexisNexis, Clearview AI.
"""

from dash import html, dcc
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from database import query_data


# Surveillance vendor data (to be moved to database)
SURVEILLANCE_VENDORS = [
    {
        'name': 'Palantir Technologies',
        'products': ['FALCON', 'Gotham', 'ICM'],
        'category': 'Data Integration & Analytics',
        'capability': 'Aggregates data from multiple sources to create profiles and track individuals. Powers ICE Investigative Case Management (ICM).',
        'ice_contract': 41000000,  # $41M
        'cbp_contract': 48000000,  # $48M
        'privacy_concern': 'Creates comprehensive surveillance profiles from disparate data sources. Used to target individuals for deportation.',
        'icon': '🔮',
    },
    {
        'name': 'LexisNexis Risk Solutions',
        'products': ['Accurint', 'CLEAR'],
        'category': 'Data Brokering',
        'capability': 'Provides access to billions of public and private records including DMV, utility, financial data.',
        'ice_contract': 22000000,  # $22M
        'cbp_contract': 15000000,  # $15M
        'privacy_concern': 'Sells personal data without consent. Helps ICE locate individuals who may have no criminal record.',
        'icon': '📊',
    },
    {
        'name': 'Thomson Reuters (CLEAR)',
        'products': ['CLEAR Investigation Software'],
        'category': 'Data Brokering',
        'capability': 'Law enforcement database providing real-time location data, phone records, social media connections.',
        'ice_contract': 12000000,
        'cbp_contract': 8000000,
        'privacy_concern': 'Provides bulk data access that circumvents warrant requirements.',
        'icon': '🔍',
    },
    {
        'name': 'Clearview AI',
        'products': ['Facial Recognition Search'],
        'category': 'Facial Recognition',
        'capability': 'Facial recognition database built from billions of scraped social media photos.',
        'ice_contract': 224000,  # Smaller contract but high impact
        'cbp_contract': 0,
        'privacy_concern': 'Scraped photos without consent. Enables identification of anyone from a photo.',
        'icon': '👁️',
    },
    {
        'name': 'Vigilant Solutions (Motorola)',
        'products': ['License Plate Recognition', 'FaceSearch'],
        'category': 'License Plate Readers',
        'capability': 'Massive database of license plate scans from cameras nationwide, tracking vehicle movements.',
        'ice_contract': 6100000,
        'cbp_contract': 3200000,
        'privacy_concern': 'Tracks vehicle movements creating detailed location histories without warrants.',
        'icon': '🚗',
    },
    {
        'name': 'Babel Street',
        'products': ['Locate X', 'Babel X'],
        'category': 'Location Tracking',
        'capability': 'Location tracking using cell phone advertising data to track individuals.',
        'ice_contract': 3500000,
        'cbp_contract': 2100000,
        'privacy_concern': 'Purchases location data from apps to track individuals without their knowledge.',
        'icon': '📍',
    },
    {
        'name': 'Venntel/Gravy Analytics',
        'products': ['Location Data Services'],
        'category': 'Location Tracking',
        'capability': 'Sells location data harvested from smartphone apps to track movements.',
        'ice_contract': 490000,
        'cbp_contract': 1100000,
        'privacy_concern': 'Apps users trusted with location data sell it to surveillance contractors.',
        'icon': '📱',
    },
    {
        'name': 'Giant Oak',
        'products': ['GOST (Giant Oak Search Technology)'],
        'category': 'Social Media Monitoring',
        'capability': 'Monitors social media posts to identify potential targets.',
        'ice_contract': 2200000,
        'cbp_contract': 0,
        'privacy_concern': 'Monitors protected speech and social media activity.',
        'icon': '💬',
    },
]

# Surveillance categories for layer cake
SURVEILLANCE_LAYERS = [
    {
        'name': 'Public Records',
        'description': 'DMV, voter registration, property records',
        'color': '#3d5a80',  # Facade blue - feels official
        'vendors': ['LexisNexis', 'Thomson Reuters'],
    },
    {
        'name': 'Commercial Data Brokering',
        'description': 'Credit, utility, phone records purchased from data brokers',
        'color': '#4a5568',  # Slate
        'vendors': ['LexisNexis', 'Thomson Reuters'],
    },
    {
        'name': 'Location Tracking',
        'description': 'Cell phone, license plate, GPS tracking',
        'color': '#718096',  # Lighter slate
        'vendors': ['Babel Street', 'Venntel', 'Vigilant Solutions'],
    },
    {
        'name': 'Biometrics & Facial Recognition',
        'description': 'Face scans, fingerprints, voice prints',
        'color': '#ed8936',  # Warning orange
        'vendors': ['Clearview AI', 'Vigilant Solutions'],
    },
    {
        'name': 'Social Media & Behavioral',
        'description': 'Posts, connections, online behavior patterns',
        'color': '#c05621',  # Burnt orange
        'vendors': ['Giant Oak', 'Babel Street'],
    },
    {
        'name': 'Integrated Surveillance Profile',
        'description': 'Palantir combines all data into actionable intelligence',
        'color': '#e53e3e',  # Truth red
        'vendors': ['Palantir'],
    },
]


def get_surveillance_tracker_content():
    """
    Main content for Surveillance Tech Stack page.
    """
    # Calculate totals
    total_ice = sum(v['ice_contract'] for v in SURVEILLANCE_VENDORS)
    total_cbp = sum(v['cbp_contract'] for v in SURVEILLANCE_VENDORS)
    total_all = total_ice + total_cbp

    return html.Div([
        # Header
        html.Div([
            html.H2("The Surveillance Tech Stack", className='section-title'),
            html.P([
                "Beyond prisons and deportation flights, a network of tech companies powers ",
                html.Strong("mass surveillance"),
                " of immigrants and citizens alike."
            ], className='section-intro'),
            html.Div([
                html.Span("🔴 ", className='live-dot'),
                html.Span("DATA COLLECTION ACTIVE", className='contested-badge')
            ], className='surveillance-alert')
        ], className='container'),

        # Totals
        html.Div([
            html.Div([
                html.Div(f"${total_all/1000000:.0f}M+", className='stat-value corporate-text'),
                html.Div("Total Surveillance Contracts", className='stat-label'),
            ], className='stat-card corporate-card'),
            html.Div([
                html.Div(f"{len(SURVEILLANCE_VENDORS)}", className='stat-value'),
                html.Div("Tech Vendors Tracked", className='stat-label'),
            ], className='stat-card'),
            html.Div([
                html.Div("6+", className='stat-value truth-text'),
                html.Div("Data Categories Monitored", className='stat-label'),
            ], className='stat-card'),
        ], className='container stats-row'),

        # Layer Cake Visualization
        html.Div([
            html.H3("The Surveillance Stack", className='subsection-title'),
            html.P([
                "Each layer represents a category of surveillance data. ",
                "Combined, they create comprehensive profiles of individuals."
            ], className='subsection-intro'),

            create_layer_cake_visualization(),

        ], className='container layer-section'),

        # Vendor Cards
        html.Div([
            html.H3("The Players", className='subsection-title'),
            html.Div([
                create_vendor_card(v) for v in SURVEILLANCE_VENDORS
            ], className='vendor-grid'),
        ], className='container vendors-section'),

        # Privacy Impact
        html.Div([
            html.H3("Why This Matters", className='context-title'),
            html.Div([
                html.Div([
                    html.Div("⚠️", className='impact-icon'),
                    html.Div([
                        html.H4("Warrantless Surveillance", className='impact-title'),
                        html.P("By purchasing data from brokers, agencies bypass 4th Amendment protections against unreasonable searches.")
                    ])
                ], className='impact-card'),
                html.Div([
                    html.Div("🎯", className='impact-icon'),
                    html.Div([
                        html.H4("Mass Data Collection", className='impact-title'),
                        html.P("Data on millions of Americans is collected regardless of any suspected wrongdoing.")
                    ])
                ], className='impact-card'),
                html.Div([
                    html.Div("🔗", className='impact-icon'),
                    html.Div([
                        html.H4("Profile Linking", className='impact-title'),
                        html.P("Disparate data sources are combined to create detailed profiles that follow individuals.")
                    ])
                ], className='impact-card'),
            ], className='impact-grid')
        ], className='container impact-section'),

    ], className='surveillance-page')


def create_layer_cake_visualization():
    """Create the layer cake stacked bar visualization."""
    fig = go.Figure()

    # Add each layer as a horizontal bar
    for i, layer in enumerate(SURVEILLANCE_LAYERS):
        fig.add_trace(go.Bar(
            y=[layer['name']],
            x=[100],  # Full width
            orientation='h',
            marker=dict(color=layer['color']),
            name=layer['name'],
            hovertemplate=f"<b>{layer['name']}</b><br>{layer['description']}<br>Vendors: {', '.join(layer['vendors'])}<extra></extra>",
            showlegend=False
        ))

    # Add person icon annotation at the bottom (being crushed)
    fig.add_annotation(
        x=50, y=-0.5,
        text="👤",
        font=dict(size=40),
        showarrow=False,
    )

    fig.add_annotation(
        x=50, y=-1.2,
        text="Your Privacy",
        font=dict(size=14, color='white'),
        showarrow=False,
    )

    fig.update_layout(
        barmode='stack',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=20, r=20, t=20, b=80),
        height=400,
        xaxis=dict(showticklabels=False, showgrid=False, zeroline=False),
        yaxis=dict(
            showgrid=False,
            tickfont=dict(color='white', size=12),
            autorange='reversed'
        ),
    )

    return dcc.Graph(
        figure=fig,
        config={'displayModeBar': False},
        className='layer-cake-chart'
    )


def create_vendor_card(vendor):
    """Create a card for a surveillance vendor."""
    total_contract = vendor['ice_contract'] + vendor['cbp_contract']

    return html.Div([
        html.Div([
            html.Span(vendor['icon'], className='vendor-icon'),
            html.Div([
                html.H4(vendor['name'], className='vendor-name'),
                html.Span(vendor['category'], className='vendor-category'),
            ])
        ], className='vendor-header'),

        html.Div([
            html.Div([
                html.Span("Products: ", className='vendor-field-label'),
                html.Span(", ".join(vendor['products']), className='vendor-field-value')
            ], className='vendor-field'),

            html.Div([
                html.Span("Capability: ", className='vendor-field-label'),
                html.Span(vendor['capability'], className='vendor-field-value')
            ], className='vendor-field'),

            html.Div([
                html.Span("Contracts: ", className='vendor-field-label'),
                html.Span(f"${total_contract/1000000:.1f}M", className='vendor-field-value corporate-text')
            ], className='vendor-field'),
        ], className='vendor-details'),

        html.Div([
            html.Span("⚠️ Privacy Concern: ", className='concern-label'),
            html.Span(vendor['privacy_concern'], className='concern-text')
        ], className='vendor-concern'),

    ], className='vendor-card')
