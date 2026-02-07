"""
Project Watchtower - Advanced Visualization Components
Provides both Plotly-based implementations and hooks for WebGL upgrades.

For production WebGL components (Deck.gl, react-force-graph), see:
- /components/webgl/README.md for custom Dash component setup
- https://dash.plotly.com/plugins for Dash component plugin guide

Current implementations use Plotly with optimizations for performance.
"""

import plotly.graph_objects as go
import plotly.express as px
from dash import html, dcc
import json
import math


# ============================================
# GLOBE / PARTICLE FLOW VISUALIZATIONS
# ============================================

def create_deportation_globe(deportation_data, show_particles=True):
    """
    Create a 3D globe visualization showing deportation flows.

    For WebGL upgrade: Replace with Deck.gl ArcLayer + ScatterplotLayer

    Args:
        deportation_data: List of dicts with keys:
            - origin_lat, origin_lon (US location)
            - dest_lat, dest_lon (destination country)
            - count (number of deportations)
            - country (destination country name)
        show_particles: Whether to animate particle effects (CSS-based)

    Returns:
        Dash component containing the globe visualization
    """
    fig = go.Figure()

    # Base globe
    fig.add_trace(go.Scattergeo(
        lon=[],
        lat=[],
        mode='markers',
        marker=dict(size=0),
        showlegend=False
    ))

    # Add arcs for each deportation route
    max_count = max(d['count'] for d in deportation_data) if deportation_data else 1

    for route in deportation_data:
        # Calculate arc points
        arc_lons, arc_lats = _calculate_great_circle_arc(
            route['origin_lon'], route['origin_lat'],
            route['dest_lon'], route['dest_lat'],
            num_points=50
        )

        # Width based on volume
        width = 1 + (route['count'] / max_count) * 4

        fig.add_trace(go.Scattergeo(
            lon=arc_lons,
            lat=arc_lats,
            mode='lines',
            line=dict(
                width=width,
                color='rgba(233, 69, 96, 0.6)'
            ),
            name=route['country'],
            hoverinfo='text',
            hovertext=f"{route['country']}: {route['count']:,} deportations"
        ))

        # Destination marker
        fig.add_trace(go.Scattergeo(
            lon=[route['dest_lon']],
            lat=[route['dest_lat']],
            mode='markers',
            marker=dict(
                size=8 + (route['count'] / max_count) * 15,
                color='rgba(233, 69, 96, 0.8)',
                line=dict(width=1, color='white')
            ),
            name=route['country'],
            hoverinfo='text',
            hovertext=f"{route['country']}<br>{route['count']:,} deportations"
        ))

    # Globe styling
    fig.update_geos(
        projection_type="orthographic",
        showland=True,
        landcolor='rgb(30, 40, 60)',
        showocean=True,
        oceancolor='rgb(15, 20, 35)',
        showlakes=False,
        showcountries=True,
        countrycolor='rgb(60, 70, 90)',
        showcoastlines=True,
        coastlinecolor='rgb(80, 90, 110)',
        bgcolor='rgba(0,0,0,0)',
        projection_rotation=dict(lon=-100, lat=40),  # Center on US
    )

    fig.update_layout(
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=0, b=0),
        height=600,
    )

    # Wrap in container with particle animation CSS
    container_class = "globe-container"
    if show_particles:
        container_class += " globe-particles-active"

    return html.Div([
        dcc.Graph(
            figure=fig,
            config={'displayModeBar': False, 'scrollZoom': True},
            className="deportation-globe"
        )
    ], className=container_class)


def _calculate_great_circle_arc(lon1, lat1, lon2, lat2, num_points=50):
    """Calculate points along a great circle arc with altitude."""
    lons = []
    lats = []

    for i in range(num_points + 1):
        f = i / num_points

        # Spherical interpolation
        lat = lat1 + f * (lat2 - lat1)
        lon = lon1 + f * (lon2 - lon1)

        # Handle dateline crossing
        if abs(lon2 - lon1) > 180:
            if lon1 > lon2:
                lon = lon1 + f * (lon2 + 360 - lon1)
            else:
                lon = lon1 + f * (lon2 - 360 - lon1)
            if lon > 180:
                lon -= 360
            elif lon < -180:
                lon += 360

        lons.append(lon)
        lats.append(lat)

    return lons, lats


# ============================================
# NETWORK GRAPH VISUALIZATIONS
# ============================================

def create_network_graph(nodes, edges, layout='force'):
    """
    Create an interactive network graph visualization.

    For WebGL upgrade: Replace with react-force-graph or vis-network

    Args:
        nodes: List of dicts with keys: id, label, type, size (optional)
        edges: List of dicts with keys: source, target, weight (optional)
        layout: 'force', 'circular', or 'hierarchical'

    Returns:
        Dash component containing the network graph
    """
    import networkx as nx

    # Build NetworkX graph
    G = nx.Graph()
    for node in nodes:
        G.add_node(node['id'], **node)
    for edge in edges:
        G.add_edge(edge['source'], edge['target'], weight=edge.get('weight', 1))

    # Calculate layout
    if layout == 'force':
        pos = nx.spring_layout(G, k=2, iterations=50)
    elif layout == 'circular':
        pos = nx.circular_layout(G)
    else:
        pos = nx.kamada_kawai_layout(G)

    # Create edge traces
    edge_traces = []
    for edge in edges:
        x0, y0 = pos[edge['source']]
        x1, y1 = pos[edge['target']]

        edge_traces.append(go.Scatter(
            x=[x0, x1, None],
            y=[y0, y1, None],
            mode='lines',
            line=dict(
                width=edge.get('weight', 1) * 0.5,
                color='rgba(150, 150, 150, 0.4)'
            ),
            hoverinfo='none'
        ))

    # Create node trace
    node_x = [pos[node['id']][0] for node in nodes]
    node_y = [pos[node['id']][1] for node in nodes]

    # Color by type
    type_colors = {
        'government': '#3d5a80',  # facade-blue
        'contractor': '#276749',  # corporate-green
        'person': '#a0aec0',      # facade-grey
        'lobbying': '#d69e2e',    # corporate-gold
    }

    node_colors = [type_colors.get(n.get('type', 'person'), '#a0aec0') for n in nodes]
    node_sizes = [n.get('size', 20) for n in nodes]
    node_labels = [n.get('label', n['id']) for n in nodes]

    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode='markers+text',
        marker=dict(
            size=node_sizes,
            color=node_colors,
            line=dict(width=2, color='white')
        ),
        text=node_labels,
        textposition='top center',
        textfont=dict(size=10, color='white'),
        hoverinfo='text',
        hovertext=[f"{n.get('label', n['id'])}<br>{n.get('type', '')}" for n in nodes]
    )

    # Create figure
    fig = go.Figure(data=edge_traces + [node_trace])

    fig.update_layout(
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        margin=dict(l=20, r=20, t=20, b=20),
        height=600,
    )

    return html.Div([
        dcc.Graph(
            figure=fig,
            config={'displayModeBar': False},
            className="network-graph"
        )
    ], className="network-container")


# ============================================
# SANKEY DIAGRAM (Budget Flows)
# ============================================

def create_budget_sankey(flow_data, title="Federal Enforcement Budget Flow"):
    """
    Create a Sankey diagram showing budget/money flows.

    Args:
        flow_data: List of dicts with keys: source, target, value, color (optional)
        title: Chart title

    Returns:
        Dash component containing the Sankey diagram
    """
    # Extract unique nodes
    sources = set(f['source'] for f in flow_data)
    targets = set(f['target'] for f in flow_data)
    all_nodes = list(sources | targets)

    # Create node indices
    node_indices = {node: i for i, node in enumerate(all_nodes)}

    # Build Sankey data
    source_indices = [node_indices[f['source']] for f in flow_data]
    target_indices = [node_indices[f['target']] for f in flow_data]
    values = [f['value'] for f in flow_data]

    # Color coding - corporate destinations in green/gold
    corporate_keywords = ['GEO', 'CORECIVIC', 'PROFIT', 'PRIVATE', 'CONTRACTOR']
    link_colors = []
    for f in flow_data:
        if any(kw in f['target'].upper() for kw in corporate_keywords):
            link_colors.append('rgba(214, 158, 46, 0.6)')  # corporate-gold
        else:
            link_colors.append('rgba(150, 150, 150, 0.4)')

    # Node colors
    node_colors = []
    for node in all_nodes:
        if any(kw in node.upper() for kw in corporate_keywords):
            node_colors.append('#276749')  # corporate-green
        elif any(kw in node.upper() for kw in ['ICE', 'CBP', 'DHS', 'GOVERNMENT']):
            node_colors.append('#3d5a80')  # facade-blue
        else:
            node_colors.append('#4a5568')  # facade-slate

    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color='rgba(255,255,255,0.3)', width=0.5),
            label=all_nodes,
            color=node_colors
        ),
        link=dict(
            source=source_indices,
            target=target_indices,
            value=values,
            color=link_colors
        )
    )])

    fig.update_layout(
        title=dict(
            text=title,
            font=dict(size=18, color='white', family='IBM Plex Sans')
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white', size=12),
        height=600,
    )

    return html.Div([
        dcc.Graph(
            figure=fig,
            config={'displayModeBar': False},
            className="sankey-chart"
        )
    ], className="sankey-container")


# ============================================
# WAFFLE CHART (Demographic Reveal)
# ============================================

def create_waffle_chart(total=1000, highlight_pct=73, labels=None):
    """
    Create a waffle chart for demographic reveals.

    Args:
        total: Total number of cells
        highlight_pct: Percentage to highlight on reveal
        labels: Dict with keys 'highlighted' and 'other' for legend

    Returns:
        Dash component with interactive waffle chart
    """
    if labels is None:
        labels = {
            'highlighted': 'No Criminal Conviction',
            'other': 'Criminal Conviction'
        }

    # Calculate grid dimensions
    cols = 50
    rows = math.ceil(total / cols)

    # Create cells
    cells = []
    for i in range(total):
        row = i // cols
        col = i % cols
        cells.append(html.Div(
            className='waffle-cell',
            **{'data-index': i}
        ))

    return html.Div([
        html.Div([
            html.Button(
                "Reveal Reality",
                id='waffle-reveal-btn',
                className='btn-export waffle-reveal-btn'
            ),
        ], className='waffle-controls'),
        html.Div(
            cells,
            className='waffle-grid',
            id='waffle-grid',
            **{
                'data-total': total,
                'data-highlight-pct': highlight_pct
            }
        ),
        html.Div([
            html.Div([
                html.Span(className='waffle-legend-color', style={'background': 'var(--success)'}),
                html.Span(labels['highlighted'])
            ], className='waffle-legend-item'),
            html.Div([
                html.Span(className='waffle-legend-color', style={'background': 'var(--facade-slate-dark)'}),
                html.Span(labels['other'])
            ], className='waffle-legend-item'),
        ], className='waffle-legend', style={'display': 'none'}, id='waffle-legend')
    ], className='waffle-container')


# ============================================
# SPLIT-SCREEN DISCREPANCY VIEW
# ============================================

def create_discrepancy_view(metric_name, official_data, independent_data, explanation):
    """
    Create a split-screen view comparing official vs independent data.

    Args:
        metric_name: Name of the metric being compared
        official_data: Dict with keys: value, display, source
        independent_data: Dict with keys: value, display, source
        explanation: Text explaining the discrepancy

    Returns:
        Dash component with split-screen comparison
    """
    return html.Div([
        html.H3(metric_name, className='discrepancy-title'),
        html.Div([
            html.Div([
                html.Div([
                    html.Span("🏛️", className='source-icon'),
                    html.Span("OFFICIAL GOVERNMENT FIGURE", className='discrepancy-label')
                ], className='discrepancy-header'),
                html.Div(official_data['display'], className='discrepancy-value'),
                html.Div(official_data['source'], className='discrepancy-source facade-text'),
                html.Div("VS", className='discrepancy-divider')
            ], className='discrepancy-side discrepancy-official'),
            html.Div([
                html.Div([
                    html.Span("✅", className='source-icon'),
                    html.Span("INDEPENDENT VERIFICATION", className='discrepancy-label')
                ], className='discrepancy-header'),
                html.Div(independent_data['display'], className='discrepancy-value truth-text'),
                html.Div(independent_data['source'], className='discrepancy-source'),
            ], className='discrepancy-side discrepancy-independent'),
        ], className='discrepancy-split'),
        html.Div([
            html.Strong("Why the difference? "),
            html.Span(explanation)
        ], className='discrepancy-explanation')
    ], className='discrepancy-container')


# ============================================
# CARTOGRAM (Distorted Map)
# ============================================

def create_detention_cartogram(state_data):
    """
    Create a cartogram where state sizes are distorted by detention population.

    Note: True cartograms require specialized libraries (topogram.js).
    This implementation uses bubble scaling as an approximation.

    Args:
        state_data: List of dicts with keys: state, value, lat, lon

    Returns:
        Dash component with cartogram visualization
    """
    max_val = max(d['value'] for d in state_data) if state_data else 1

    fig = go.Figure()

    # Add choropleth base
    fig.add_trace(go.Choropleth(
        locations=[d['state'] for d in state_data],
        z=[d['value'] for d in state_data],
        locationmode='USA-states',
        colorscale=[
            [0, 'rgb(30, 40, 60)'],
            [0.5, 'rgb(100, 50, 70)'],
            [1, 'rgb(229, 62, 62)']
        ],
        showscale=True,
        colorbar=dict(
            title='Detained<br>Population',
            titlefont=dict(color='white'),
            tickfont=dict(color='white')
        )
    ))

    # Add scaled bubbles for cartogram effect
    for d in state_data:
        size = 10 + (d['value'] / max_val) * 50

        fig.add_trace(go.Scattergeo(
            lon=[d['lon']],
            lat=[d['lat']],
            mode='markers',
            marker=dict(
                size=size,
                color='rgba(229, 62, 62, 0.6)',
                line=dict(width=1, color='white')
            ),
            hoverinfo='text',
            hovertext=f"{d['state']}: {d['value']:,}",
            showlegend=False
        ))

    fig.update_geos(
        scope='usa',
        showland=True,
        landcolor='rgb(30, 40, 60)',
        showlakes=False,
        bgcolor='rgba(0,0,0,0)'
    )

    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=30, b=0),
        height=500,
        title=dict(
            text='Detention Population by State',
            font=dict(color='white', size=16)
        )
    )

    return html.Div([
        dcc.Graph(
            figure=fig,
            config={'displayModeBar': False},
            className="cartogram-chart"
        )
    ], className="cartogram-container")


# ============================================
# ISOTYPE CHART (Staffing Growth)
# ============================================

def create_isotype_timeline(timeline_data, icon="👤"):
    """
    Create an isotype visualization showing growth over time.

    Args:
        timeline_data: List of dicts with keys: year, value, label
        icon: Icon/emoji to use for each unit

    Returns:
        Dash component with isotype visualization
    """
    max_val = max(d['value'] for d in timeline_data) if timeline_data else 1
    scale_factor = 100  # Each icon represents this many people

    timeline_elements = []

    for data in timeline_data:
        num_icons = data['value'] // scale_factor
        icon_row = icon * min(num_icons, 50)  # Cap at 50 per row

        # Multiple rows if needed
        rows = []
        remaining = num_icons
        while remaining > 0:
            row_count = min(remaining, 50)
            rows.append(html.Div(icon * row_count, className='isotype-row'))
            remaining -= row_count

        timeline_elements.append(html.Div([
            html.Div(str(data['year']), className='isotype-year'),
            html.Div(rows, className='isotype-icons'),
            html.Div(f"{data['value']:,}", className='isotype-value'),
        ], className='isotype-period'))

    return html.Div([
        html.Div(f"Each {icon} = {scale_factor:,} personnel", className='isotype-legend'),
        html.Div(timeline_elements, className='isotype-timeline')
    ], className='isotype-container')
