"""
Project Watchtower - Revolving Door Network Graph
FR 3.3: Visualize personnel flows between government and industry

Visual Strategy: Interactive network graph showing personnel moving
between ICE/DHS and private contractors. Node size by influence,
edge thickness by connection strength.
"""

import plotly.graph_objects as go
try:
    import networkx as nx
except ImportError:
    nx = None
from dash import html, dcc
import math

# Import data
import sys
sys.path.insert(0, '..')
try:
    from data.revolving_door import get_revolving_door_db, get_revolving_door_network
except ImportError:
    # Fallback for direct import
    from data.revolving_door import get_revolving_door_db, get_revolving_door_network


# Color palette
COLORS = {
    'bg': '#0f0f23',
    'government': '#3d5a80',
    'industry': '#276749',
    'person': '#ed8936',
    'lobbyist': '#9b2c2c',
    'edge_personnel': 'rgba(237, 137, 54, 0.4)',
    'edge_lobbying': 'rgba(155, 44, 44, 0.4)',
    'edge_money': 'rgba(214, 158, 46, 0.4)',
    'text': '#e2e8f0',
    'text_muted': '#8d99ae',
}


def create_revolving_door_network():
    """Create the network visualization."""
    db = get_revolving_door_db()
    network_data = db.build_network_graph()

    # Build NetworkX graph
    G = nx.DiGraph()

    for node in network_data['nodes']:
        G.add_node(node['id'], **node)

    for edge in network_data['edges']:
        G.add_edge(edge['source'], edge['target'], **edge)

    # Use spring layout
    pos = nx.spring_layout(G, k=2, iterations=50, seed=42)

    # Create edge traces by type
    edge_traces = []

    edge_types = {
        'personnel_flow': {'color': COLORS['edge_personnel'], 'dash': 'solid'},
        'lobbying': {'color': COLORS['edge_lobbying'], 'dash': 'dot'},
        'campaign_contributions': {'color': COLORS['edge_money'], 'dash': 'dash'},
        'former_employee': {'color': COLORS['edge_personnel'], 'dash': 'solid'},
        'current_employee': {'color': COLORS['person'], 'dash': 'solid'},
    }

    for edge_type, style in edge_types.items():
        edge_x = []
        edge_y = []

        for edge in G.edges(data=True):
            if edge[2].get('type') == edge_type:
                x0, y0 = pos[edge[0]]
                x1, y1 = pos[edge[1]]
                edge_x.extend([x0, x1, None])
                edge_y.extend([y0, y1, None])

        if edge_x:
            edge_traces.append(go.Scatter(
                x=edge_x, y=edge_y,
                mode='lines',
                line=dict(width=2, color=style['color'], dash=style['dash']),
                hoverinfo='none',
                showlegend=False,
            ))

    # Create node traces by type
    node_traces = []

    node_types = {
        'government': {'color': COLORS['government'], 'size': 35, 'symbol': 'square'},
        'industry': {'color': COLORS['industry'], 'size': 35, 'symbol': 'diamond'},
        'person': {'color': COLORS['person'], 'size': 20, 'symbol': 'circle'},
    }

    for node_type, style in node_types.items():
        type_nodes = [n for n, d in G.nodes(data=True) if d.get('type') == node_type]
        if not type_nodes:
            continue

        node_x = [pos[n][0] for n in type_nodes]
        node_y = [pos[n][1] for n in type_nodes]
        node_labels = [G.nodes[n].get('label', n) for n in type_nodes]

        node_traces.append(go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            marker=dict(
                size=style['size'],
                color=style['color'],
                symbol=style['symbol'],
                line=dict(width=2, color='white'),
            ),
            text=node_labels,
            textposition='bottom center',
            textfont=dict(size=10, color='white'),
            hovertemplate='<b>%{text}</b><extra></extra>',
            name=node_type.title(),
        ))

    fig = go.Figure(data=edge_traces + node_traces)

    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor=COLORS['bg'],
        plot_bgcolor=COLORS['bg'],
        font=dict(family='IBM Plex Sans, sans-serif', color=COLORS['text']),
        title=dict(
            text='<b>The Revolving Door</b><br>'
                 '<sup>Personnel flows between government and private contractors</sup>',
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
        height=550,
    )

    return fig


def create_person_card(person):
    """Create a card for a revolving door person."""
    if person['type'] == 'gov_to_industry':
        gov_role = person['government_role']
        ind_role = person['industry_role']

        return html.Div([
            html.H4(person['name'], className='person-name'),
            html.Div([
                html.Div([
                    html.Span("Government", className='role-type gov'),
                    html.Div(gov_role['position'], className='role-title'),
                    html.Div(f"{gov_role['agency']} ({gov_role['years']})", className='role-org'),
                ], className='role-section'),
                html.Div("→", className='flow-arrow'),
                html.Div([
                    html.Span("Industry", className='role-type ind'),
                    html.Div(ind_role['position'], className='role-title'),
                    html.Div(f"{ind_role['company']} ({ind_role['years']})", className='role-org'),
                ], className='role-section'),
            ], className='role-flow'),
            html.P(person['significance'], className='person-significance'),
            html.Div(f"Source: {person['source']}", className='person-source'),
        ], className='person-card')

    elif person['type'] == 'lobbyist':
        return html.Div([
            html.H4(person['name'], className='person-name'),
            html.Span("Lobbyist", className='role-type lobbyist'),
            html.Div(f"Firm: {person['firm']}", className='role-org'),
            html.Div(f"Clients: {', '.join(person['clients'])}", className='role-clients'),
            html.P(person['significance'], className='person-significance'),
        ], className='person-card lobbyist-card')

    return html.Div()


def get_revolving_door_content():
    """
    Build and return the Revolving Door Network page.

    Returns:
        Dash html.Div with the network visualization
    """
    db = get_revolving_door_db()
    stats = db.get_summary_stats()
    gov_to_industry = db.get_gov_to_industry()[:6]
    lobbyists = db.get_lobbyists()[:4]

    network_fig = create_revolving_door_network()
    person_cards = [create_person_card(p) for p in gov_to_industry]
    lobbyist_cards = [create_person_card(p) for p in lobbyists]

    return html.Div([
        # Header
        html.Div([
            html.Div([
                html.H2("The Revolving Door", className='section-title'),
                html.P([
                    "When the same people move back and forth between regulating an industry ",
                    "and profiting from it, whose interests do they serve? This network maps ",
                    "the flow of personnel between ICE/DHS and private detention companies."
                ], className='section-intro'),
            ], className='container'),
        ], className='door-header'),

        # Key statistics
        html.Div([
            html.Div([
                html.Div([
                    html.Div([
                        html.Span("Personnel Tracked", className='stat-label'),
                        html.Span(f"{stats['total_personnel_tracked']}", className='stat-value'),
                    ], className='door-stat'),
                    html.Div([
                        html.Span("Gov → Industry", className='stat-label'),
                        html.Span(f"{stats['gov_to_industry_count']}", className='stat-value stat-warning'),
                    ], className='door-stat'),
                    html.Div([
                        html.Span("Lobbyists", className='stat-label'),
                        html.Span(f"{stats['lobbyists_tracked']}", className='stat-value'),
                    ], className='door-stat'),
                    html.Div([
                        html.Span("Connections", className='stat-label'),
                        html.Span(f"{stats['total_connections']}", className='stat-value'),
                    ], className='door-stat'),
                ], className='door-stats-row'),
            ], className='container'),
        ], className='door-stats-bar'),

        # Network visualization
        html.Div([
            html.Div([
                dcc.Graph(
                    id='revolving-door-network',
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
                        html.Span(className='legend-marker', style={'backgroundColor': COLORS['government']}),
                        html.Span("Government Agency", className='legend-label'),
                    ], className='legend-item'),
                    html.Div([
                        html.Span(className='legend-marker', style={'backgroundColor': COLORS['industry']}),
                        html.Span("Private Company", className='legend-label'),
                    ], className='legend-item'),
                    html.Div([
                        html.Span(className='legend-marker', style={'backgroundColor': COLORS['person']}),
                        html.Span("Individual", className='legend-label'),
                    ], className='legend-item'),
                ], className='legend-row'),
            ], className='container'),
        ], className='legend-section'),

        # Key finding callout
        html.Div([
            html.Div([
                html.Div([
                    html.H3("Key Finding", className='callout-title'),
                    html.P([
                        html.Strong(stats['key_finding']),
                        " These aren't mid-level employees—they're executives who shaped detention policy ",
                        "and now profit from it. When they lobbied for expanding detention while at ICE, ",
                        "were they serving the public interest or building their future employer's market?"
                    ], className='callout-text'),
                ], className='finding-box'),
            ], className='container'),
        ], className='finding-section'),

        # Personnel cards
        html.Div([
            html.Div([
                html.H3("Government to Industry", className='subsection-title'),
                html.Div(person_cards, className='personnel-grid'),
            ], className='container'),
        ], className='personnel-section'),

        # Lobbyist cards
        html.Div([
            html.Div([
                html.H3("Key Lobbyists", className='subsection-title'),
                html.Div(lobbyist_cards, className='personnel-grid'),
            ], className='container'),
        ], className='lobbyists-section'),

        # Methodology
        html.Div([
            html.Div([
                html.H4("Data Sources", className='methodology-title'),
                html.P([
                    "Personnel data compiled from LinkedIn profiles, SEC filings (Form 10-K, DEF 14A), ",
                    "lobbying disclosure databases (LDA filings), news investigations, and FOIA releases. ",
                    "Network connections verified through multiple sources where possible."
                ], className='methodology-text'),
            ], className='container'),
        ], className='door-methodology'),

    ], className='revolving-door-page')
