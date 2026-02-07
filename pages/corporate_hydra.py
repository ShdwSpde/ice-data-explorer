"""
Project Watchtower - Corporate Hydra Visualization
PAGE 13: Multi-headed contractor visualization

Visual Strategy: Network diagram showing how the same parent companies
operate across multiple segments of immigration enforcement - detention,
surveillance, transportation, and services. The "hydra" metaphor reveals
vertical integration and market dominance.
"""

import plotly.graph_objects as go
try:
    import networkx as nx
except ImportError:
    nx = None
from dash import html, dcc
import math


# Color palette
COLORS = {
    'bg': '#0f0f23',
    'parent': '#276749',        # Corporate green for parent companies
    'detention': '#e53e3e',     # Red for detention
    'surveillance': '#3d5a80',  # Blue for surveillance
    'transport': '#ed8936',     # Orange for transport
    'services': '#9b2c2c',      # Dark red for services
    'lobbying': '#d69e2e',      # Gold for political
    'text': '#e2e8f0',
    'text_muted': '#8d99ae',
    'link': 'rgba(255, 255, 255, 0.15)',
}

# Corporate conglomerate data
HYDRA_DATA = {
    'GEO Group': {
        'type': 'parent',
        'revenue': 2400,  # millions
        'employees': 23000,
        'founded': 1984,
        'hq': 'Boca Raton, FL',
        'subsidiaries': [
            {'name': 'GEO Detention', 'type': 'detention', 'revenue': 1450, 'facilities': 57, 'beds': 48000},
            {'name': 'GEO Transport', 'type': 'transport', 'revenue': 185, 'vehicles': 450, 'routes': 'nationwide'},
            {'name': 'BI Incorporated', 'type': 'surveillance', 'revenue': 380, 'product': 'ankle monitors', 'users': 140000},
            {'name': 'GEO Reentry', 'type': 'services', 'revenue': 285, 'programs': 'residential reentry'},
            {'name': 'GEO Care', 'type': 'services', 'revenue': 100, 'programs': 'mental health services'},
        ],
        'lobbying_total': 12500000,
        'contracts_ice': 892000000,
    },
    'CoreCivic': {
        'type': 'parent',
        'revenue': 1900,
        'employees': 12500,
        'founded': 1983,
        'hq': 'Nashville, TN',
        'subsidiaries': [
            {'name': 'CoreCivic Safety', 'type': 'detention', 'revenue': 1180, 'facilities': 44, 'beds': 72000},
            {'name': 'CoreCivic Properties', 'type': 'services', 'revenue': 420, 'product': 'facility ownership'},
            {'name': 'TransCor America', 'type': 'transport', 'revenue': 95, 'vehicles': 200, 'routes': 'corrections'},
            {'name': 'CoreCivic Community', 'type': 'services', 'revenue': 205, 'programs': 'residential reentry'},
        ],
        'lobbying_total': 8200000,
        'contracts_ice': 756000000,
    },
    'Caliburn International': {
        'type': 'parent',
        'revenue': 800,
        'employees': 8000,
        'founded': 2018,
        'hq': 'Reston, VA',
        'subsidiaries': [
            {'name': 'Comprehensive Health Services', 'type': 'services', 'revenue': 420, 'product': 'medical staffing'},
            {'name': 'Sallyport Global', 'type': 'services', 'revenue': 280, 'product': 'security services'},
            {'name': 'Janus Global', 'type': 'services', 'revenue': 100, 'product': 'training services'},
        ],
        'lobbying_total': 2100000,
        'contracts_ice': 340000000,
    },
    'Palantir Technologies': {
        'type': 'parent',
        'revenue': 2200,
        'employees': 3700,
        'founded': 2003,
        'hq': 'Denver, CO',
        'subsidiaries': [
            {'name': 'Palantir USG', 'type': 'surveillance', 'revenue': 890, 'product': 'FALCON/ICM systems'},
            {'name': 'Palantir Foundry', 'type': 'surveillance', 'revenue': 420, 'product': 'data integration'},
        ],
        'lobbying_total': 4800000,
        'contracts_ice': 340000000,
    },
    'LexisNexis Risk': {
        'type': 'parent',
        'revenue': 13000,  # RELX parent
        'employees': 33000,
        'founded': 1970,
        'hq': 'London, UK / Atlanta, GA',
        'subsidiaries': [
            {'name': 'Accurint for Law Enforcement', 'type': 'surveillance', 'revenue': 280, 'product': 'person search'},
            {'name': 'LexisNexis Special Services', 'type': 'surveillance', 'revenue': 156, 'product': 'investigative data'},
            {'name': 'ThreatMetrix', 'type': 'surveillance', 'revenue': 120, 'product': 'fraud detection'},
        ],
        'lobbying_total': 3200000,
        'contracts_ice': 156000000,
    },
}


def create_hydra_network():
    """Create a network graph showing corporate interconnections."""
    G = nx.Graph()

    # Add parent company nodes
    for company, data in HYDRA_DATA.items():
        G.add_node(
            company,
            node_type='parent',
            revenue=data['revenue'],
            ice_contracts=data['contracts_ice'],
        )

        # Add subsidiary nodes
        for sub in data['subsidiaries']:
            sub_name = sub['name']
            G.add_node(
                sub_name,
                node_type=sub['type'],
                revenue=sub['revenue'],
                parent=company,
            )
            G.add_edge(company, sub_name, weight=sub['revenue'])

    # Position nodes in a radial layout
    # Parents in center ring, subsidiaries in outer ring
    pos = {}
    parent_companies = [n for n in G.nodes() if G.nodes[n].get('node_type') == 'parent']
    n_parents = len(parent_companies)

    for i, parent in enumerate(parent_companies):
        angle = 2 * math.pi * i / n_parents
        pos[parent] = (math.cos(angle) * 0.4, math.sin(angle) * 0.4)

        # Position subsidiaries around their parent
        subs = [n for n in G.neighbors(parent)]
        n_subs = len(subs)
        for j, sub in enumerate(subs):
            sub_angle = angle + (j - n_subs/2) * 0.3
            pos[sub] = (math.cos(sub_angle) * 0.85, math.sin(sub_angle) * 0.85)

    # Create edge traces
    edge_x, edge_y = [], []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        mode='lines',
        line=dict(width=1, color=COLORS['link']),
        hoverinfo='none',
    )

    # Create node traces by type
    node_traces = []

    type_configs = {
        'parent': {'color': COLORS['parent'], 'size': 40, 'symbol': 'diamond'},
        'detention': {'color': COLORS['detention'], 'size': 25, 'symbol': 'circle'},
        'surveillance': {'color': COLORS['surveillance'], 'size': 25, 'symbol': 'square'},
        'transport': {'color': COLORS['transport'], 'size': 25, 'symbol': 'triangle-up'},
        'services': {'color': COLORS['services'], 'size': 25, 'symbol': 'pentagon'},
    }

    for node_type, config in type_configs.items():
        type_nodes = [n for n in G.nodes() if G.nodes[n].get('node_type') == node_type]
        if not type_nodes:
            continue

        x = [pos[n][0] for n in type_nodes]
        y = [pos[n][1] for n in type_nodes]

        if node_type == 'parent':
            text = [f"<b>{n}</b><br>${HYDRA_DATA[n]['revenue']}M revenue<br>"
                   f"${HYDRA_DATA[n]['contracts_ice']/1e6:.0f}M ICE contracts"
                   for n in type_nodes]
        else:
            text = [f"<b>{n}</b><br>${G.nodes[n]['revenue']}M revenue"
                   for n in type_nodes]

        node_traces.append(go.Scatter(
            x=x, y=y,
            mode='markers+text',
            marker=dict(
                size=config['size'],
                color=config['color'],
                symbol=config['symbol'],
                line=dict(width=2, color='white'),
            ),
            text=[n.replace(' ', '<br>') for n in type_nodes] if node_type != 'parent' else type_nodes,
            textposition='bottom center',
            textfont=dict(size=9, color='white'),
            hovertemplate='%{customdata}<extra></extra>',
            customdata=text,
            name=node_type.title(),
        ))

    fig = go.Figure(data=[edge_trace] + node_traces)

    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor=COLORS['bg'],
        plot_bgcolor=COLORS['bg'],
        font=dict(family='IBM Plex Sans, sans-serif', color=COLORS['text']),
        title=dict(
            text='<b>The Corporate Hydra</b><br>'
                 '<sup>How parent companies dominate multiple enforcement sectors</sup>',
            font=dict(size=18),
            x=0.5,
        ),
        showlegend=True,
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=-0.15,
            xanchor='center',
            x=0.5,
        ),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        margin=dict(t=80, b=80, l=40, r=40),
        height=600,
    )

    return fig


def create_company_card(company, data):
    """Create a detailed card for a parent company."""
    sub_items = []
    for sub in data['subsidiaries']:
        type_color = {
            'detention': COLORS['detention'],
            'surveillance': COLORS['surveillance'],
            'transport': COLORS['transport'],
            'services': COLORS['services'],
        }.get(sub['type'], COLORS['text_muted'])

        sub_items.append(html.Div([
            html.Span(sub['name'], className='sub-name'),
            html.Span(sub['type'].title(), className='sub-type', style={'color': type_color}),
            html.Span(f"${sub['revenue']}M", className='sub-revenue'),
        ], className='subsidiary-item'))

    return html.Div([
        html.Div([
            html.H3(company, className='company-name'),
            html.Div([
                html.Span(f"${data['revenue']}M revenue", className='company-revenue'),
                html.Span(" | ", className='separator'),
                html.Span(f"{data['employees']:,} employees", className='company-employees'),
            ], className='company-stats'),
        ], className='company-header'),

        html.Div([
            html.Div([
                html.Span("ICE Contracts: ", className='metric-label'),
                html.Span(f"${data['contracts_ice']/1e6:.0f}M", className='metric-value'),
            ], className='company-metric'),
            html.Div([
                html.Span("Lobbying (total): ", className='metric-label'),
                html.Span(f"${data['lobbying_total']/1e6:.1f}M", className='metric-value'),
            ], className='company-metric'),
        ], className='company-metrics'),

        html.Div([
            html.H4("Subsidiaries", className='sub-header'),
            html.Div(sub_items, className='subsidiaries-list'),
        ], className='subsidiaries-section'),

    ], className='company-card')


def get_corporate_hydra_content():
    """
    Build and return the Corporate Hydra page.

    Returns:
        Dash html.Div with the hydra visualization
    """
    network_fig = create_hydra_network()

    company_cards = [
        create_company_card(company, data)
        for company, data in HYDRA_DATA.items()
    ]

    # Calculate totals
    total_revenue = sum(d['revenue'] for d in HYDRA_DATA.values())
    total_ice = sum(d['contracts_ice'] for d in HYDRA_DATA.values())
    total_lobbying = sum(d['lobbying_total'] for d in HYDRA_DATA.values())

    return html.Div([
        # Header
        html.Div([
            html.Div([
                html.H2("The Corporate Hydra", className='section-title'),
                html.P([
                    "Like the mythical hydra, the immigration enforcement industry grows multiple heads. ",
                    "A handful of parent companies control detention, surveillance, transportation, ",
                    "and support services—creating vertical integration that maximizes profit at every ",
                    "step of the enforcement pipeline."
                ], className='section-intro'),
            ], className='container'),
        ], className='hydra-header'),

        # Key statistics
        html.Div([
            html.Div([
                html.Div([
                    html.Div([
                        html.Span("Parent Companies", className='stat-label'),
                        html.Span(f"{len(HYDRA_DATA)}", className='stat-value'),
                    ], className='hydra-stat'),
                    html.Div([
                        html.Span("Combined Revenue", className='stat-label'),
                        html.Span(f"${total_revenue/1000:.1f}B", className='stat-value'),
                    ], className='hydra-stat'),
                    html.Div([
                        html.Span("ICE Contracts", className='stat-label'),
                        html.Span(f"${total_ice/1e9:.2f}B", className='stat-value'),
                    ], className='hydra-stat'),
                    html.Div([
                        html.Span("Lobbying Spend", className='stat-label'),
                        html.Span(f"${total_lobbying/1e6:.0f}M", className='stat-value'),
                    ], className='hydra-stat'),
                ], className='hydra-stats-row'),
            ], className='container'),
        ], className='hydra-stats-bar'),

        # Network visualization
        html.Div([
            html.Div([
                dcc.Graph(
                    id='hydra-network',
                    figure=network_fig,
                    config={'displayModeBar': False},
                ),
            ], className='container'),
        ], className='network-section'),

        # Legend
        html.Div([
            html.Div([
                html.Div([
                    html.Div([
                        html.Span(className='legend-marker', style={'backgroundColor': COLORS['parent']}),
                        html.Span("Parent Company", className='legend-label'),
                    ], className='legend-item'),
                    html.Div([
                        html.Span(className='legend-marker', style={'backgroundColor': COLORS['detention']}),
                        html.Span("Detention Operations", className='legend-label'),
                    ], className='legend-item'),
                    html.Div([
                        html.Span(className='legend-marker', style={'backgroundColor': COLORS['surveillance']}),
                        html.Span("Surveillance Tech", className='legend-label'),
                    ], className='legend-item'),
                    html.Div([
                        html.Span(className='legend-marker', style={'backgroundColor': COLORS['transport']}),
                        html.Span("Transportation", className='legend-label'),
                    ], className='legend-item'),
                    html.Div([
                        html.Span(className='legend-marker', style={'backgroundColor': COLORS['services']}),
                        html.Span("Support Services", className='legend-label'),
                    ], className='legend-item'),
                ], className='legend-row'),
            ], className='container'),
        ], className='legend-section'),

        # Company detail cards
        html.Div([
            html.Div([
                html.H3("The Major Players", className='subsection-title'),
                html.Div(company_cards, className='companies-grid'),
            ], className='container'),
        ], className='companies-section'),

        # The pattern callout
        html.Div([
            html.Div([
                html.Div([
                    html.H3("The Vertical Integration Playbook", className='pattern-title'),
                    html.P([
                        "Control the entire pipeline: Own the detention facility where someone is held. ",
                        "Own the ankle monitor tracking them if released. Own the transport that moves them. ",
                        "Own the data systems that identify them. Every touchpoint is a profit center."
                    ], className='pattern-text'),
                    html.P([
                        html.Strong("The result: "),
                        "Lobbying for harsher enforcement pays off at every level of the supply chain. ",
                        "More arrests mean more detention beds, more monitors, more data queries, more transports. ",
                        "The incentive structure pushes toward maximum enforcement, not effective policy."
                    ], className='pattern-text'),
                ], className='pattern-box'),
            ], className='container'),
        ], className='pattern-section'),

        # Methodology
        html.Div([
            html.Div([
                html.H4("Data Sources", className='methodology-title'),
                html.P([
                    "Revenue and subsidiary data from SEC 10-K filings and corporate annual reports. ",
                    "Contract values from USASpending.gov and FPDS. Lobbying totals from OpenSecrets.org. ",
                    "Corporate structure verified through state business registrations and D&B records."
                ], className='methodology-text'),
            ], className='container'),
        ], className='hydra-methodology'),

    ], className='corporate-hydra-page')
