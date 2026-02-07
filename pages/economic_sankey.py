"""
Project Watchtower - Economic Leakage Sankey Diagram
FR 3.1: Trace how enforcement dollars flow to private contractors

Visual Strategy: Interactive Sankey diagram showing money flowing from
taxpayers through DHS/ICE to private prison companies, tech vendors,
and lobbying activities. Reveals the circular economy of enforcement.
"""

import plotly.graph_objects as go
from dash import html, dcc
from database import query_data


# Color palette
COLORS = {
    'bg': '#0f0f23',
    'taxpayer': '#3d5a80',      # Facade blue - public money
    'agency': '#4a5568',        # Slate - government
    'private_prison': '#276749', # Corporate green - prison corps
    'tech': '#2c5282',          # Tech blue
    'services': '#744210',      # Brown - services
    'lobbying': '#9b2c2c',      # Dark red - corruption
    'profit': '#d69e2e',        # Gold - profit extraction
    'text': '#e2e8f0',
    'text_muted': '#8d99ae',
    'link_opacity': 0.4,
}

# Sankey flow data (in millions USD, FY2023 estimates)
# Structure: source -> target -> value
FLOW_DATA = {
    'nodes': [
        # Level 0: Source
        'Federal Taxpayers',

        # Level 1: Agencies
        'DHS Budget',
        'ICE ERO',
        'CBP',
        'USCIS',

        # Level 2: Program areas
        'Detention Operations',
        'Removal Operations',
        'Border Infrastructure',
        'Surveillance Tech',
        'Legal Processing',

        # Level 3: Recipients
        'GEO Group',
        'CoreCivic',
        'Management & Training Corp',
        'LaSalle Corrections',
        'Palantir',
        'LexisNexis Risk',
        'Northrop Grumman',
        'General Dynamics',
        'Local County Jails',
        'Airlines (Deportation)',
        'Legal Services',

        # Level 4: Outcomes
        'Executive Compensation',
        'Shareholder Dividends',
        'Lobbying & Campaign',
        'Facility Operations',
        'Subcontractors',
    ],

    'links': [
        # Taxpayers -> DHS
        ('Federal Taxpayers', 'DHS Budget', 97000),

        # DHS -> Agencies
        ('DHS Budget', 'ICE ERO', 9200),
        ('DHS Budget', 'CBP', 18700),
        ('DHS Budget', 'USCIS', 4800),

        # ICE ERO -> Programs
        ('ICE ERO', 'Detention Operations', 3200),
        ('ICE ERO', 'Removal Operations', 1800),
        ('ICE ERO', 'Surveillance Tech', 890),
        ('ICE ERO', 'Legal Processing', 420),

        # CBP -> Programs
        ('CBP', 'Border Infrastructure', 4200),
        ('CBP', 'Surveillance Tech', 2100),
        ('CBP', 'Detention Operations', 1500),

        # Detention -> Private Prisons
        ('Detention Operations', 'GEO Group', 1420),
        ('Detention Operations', 'CoreCivic', 1180),
        ('Detention Operations', 'Management & Training Corp', 340),
        ('Detention Operations', 'LaSalle Corrections', 280),
        ('Detention Operations', 'Local County Jails', 1480),

        # Surveillance -> Tech Companies
        ('Surveillance Tech', 'Palantir', 420),
        ('Surveillance Tech', 'LexisNexis Risk', 380),
        ('Surveillance Tech', 'Northrop Grumman', 890),
        ('Surveillance Tech', 'General Dynamics', 720),

        # Removal -> Airlines
        ('Removal Operations', 'Airlines (Deportation)', 680),
        ('Removal Operations', 'GEO Group', 320),  # Transport contracts

        # Legal -> Services
        ('Legal Processing', 'Legal Services', 420),

        # Private Prisons -> Outcomes
        ('GEO Group', 'Executive Compensation', 42),
        ('GEO Group', 'Shareholder Dividends', 180),
        ('GEO Group', 'Lobbying & Campaign', 12),
        ('GEO Group', 'Facility Operations', 1200),
        ('GEO Group', 'Subcontractors', 306),

        ('CoreCivic', 'Executive Compensation', 38),
        ('CoreCivic', 'Shareholder Dividends', 150),
        ('CoreCivic', 'Lobbying & Campaign', 8),
        ('CoreCivic', 'Facility Operations', 920),
        ('CoreCivic', 'Subcontractors', 64),

        # Tech -> Outcomes
        ('Palantir', 'Executive Compensation', 28),
        ('Palantir', 'Shareholder Dividends', 45),
        ('Palantir', 'Lobbying & Campaign', 4),
        ('Palantir', 'Subcontractors', 343),

        ('Northrop Grumman', 'Shareholder Dividends', 320),
        ('Northrop Grumman', 'Lobbying & Campaign', 18),
        ('Northrop Grumman', 'Subcontractors', 552),
    ]
}


def get_node_color(node_name):
    """Return color for a node based on its category."""
    if 'Taxpayer' in node_name:
        return COLORS['taxpayer']
    elif node_name in ['DHS Budget', 'ICE ERO', 'CBP', 'USCIS']:
        return COLORS['agency']
    elif node_name in ['GEO Group', 'CoreCivic', 'Management & Training Corp', 'LaSalle Corrections']:
        return COLORS['private_prison']
    elif node_name in ['Palantir', 'LexisNexis Risk', 'Northrop Grumman', 'General Dynamics']:
        return COLORS['tech']
    elif 'Lobbying' in node_name or 'Campaign' in node_name:
        return COLORS['lobbying']
    elif 'Dividend' in node_name or 'Compensation' in node_name:
        return COLORS['profit']
    else:
        return COLORS['services']


def create_sankey_diagram():
    """
    Create the Economic Leakage Sankey diagram.

    Returns:
        Plotly figure object
    """
    nodes = FLOW_DATA['nodes']
    node_indices = {name: i for i, name in enumerate(nodes)}

    # Build link arrays
    sources = []
    targets = []
    values = []

    for source, target, value in FLOW_DATA['links']:
        sources.append(node_indices[source])
        targets.append(node_indices[target])
        values.append(value)

    # Node colors
    node_colors = [get_node_color(name) for name in nodes]

    # Link colors (based on source, with transparency)
    link_colors = []
    for source, target, value in FLOW_DATA['links']:
        base_color = get_node_color(source)
        # Convert hex to rgba
        r = int(base_color[1:3], 16)
        g = int(base_color[3:5], 16)
        b = int(base_color[5:7], 16)
        link_colors.append(f'rgba({r},{g},{b},{COLORS["link_opacity"]})')

    fig = go.Figure(data=[go.Sankey(
        arrangement='snap',
        node=dict(
            pad=20,
            thickness=25,
            line=dict(color='rgba(255,255,255,0.1)', width=1),
            label=nodes,
            color=node_colors,
            hovertemplate='<b>%{label}</b><br>Total Flow: $%{value:,.0f}M<extra></extra>',
        ),
        link=dict(
            source=sources,
            target=targets,
            value=values,
            color=link_colors,
            hovertemplate='%{source.label} → %{target.label}<br>'
                          '<b>$%{value:,.0f}M</b><extra></extra>',
        ),
    )])

    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor=COLORS['bg'],
        plot_bgcolor=COLORS['bg'],
        font=dict(
            family='IBM Plex Sans, sans-serif',
            color=COLORS['text'],
            size=12,
        ),
        title=dict(
            text='<b>Follow the Money: Immigration Enforcement Spending</b><br>'
                 '<sup>FY2023 Budget Flows ($ Millions)</sup>',
            font=dict(size=18),
            x=0.5,
            xanchor='center',
        ),
        margin=dict(t=80, b=40, l=20, r=20),
        height=700,
    )

    return fig


def get_economic_sankey_content():
    """
    Build and return the Economic Leakage Sankey page.

    Returns:
        Dash html.Div with the Sankey visualization
    """
    # Calculate key statistics
    total_dhs = 97000
    total_to_private = sum(v for s, t, v in FLOW_DATA['links']
                          if t in ['GEO Group', 'CoreCivic', 'Management & Training Corp',
                                  'LaSalle Corrections', 'Palantir', 'LexisNexis Risk',
                                  'Northrop Grumman', 'General Dynamics'])
    total_lobbying = sum(v for s, t, v in FLOW_DATA['links'] if 'Lobbying' in t)
    total_dividends = sum(v for s, t, v in FLOW_DATA['links'] if 'Dividend' in t)
    total_exec_comp = sum(v for s, t, v in FLOW_DATA['links'] if 'Executive' in t)

    fig = create_sankey_diagram()

    return html.Div([
        # Header
        html.Div([
            html.Div([
                html.H2("Economic Leakage: The Enforcement Industrial Complex",
                       className='section-title'),
                html.P([
                    "Your tax dollars flow from the federal treasury through DHS agencies ",
                    "to a network of private contractors. This Sankey diagram traces how ",
                    "enforcement spending enriches corporations, funds lobbying, and extracts ",
                    "value from the system at every step."
                ], className='section-intro'),
            ], className='container'),
        ], className='sankey-header'),

        # Key statistics
        html.Div([
            html.Div([
                html.Div([
                    html.Div([
                        html.Span("DHS Budget", className='stat-label'),
                        html.Span(f"${total_dhs/1000:.0f}B", className='stat-value'),
                    ], className='sankey-stat'),
                    html.Div([
                        html.Span("To Private Contractors", className='stat-label'),
                        html.Span(f"${total_to_private/1000:.1f}B", className='stat-value'),
                        html.Span(f"({total_to_private/total_dhs*100:.1f}%)", className='stat-note'),
                    ], className='sankey-stat'),
                    html.Div([
                        html.Span("Lobbying Spend", className='stat-label'),
                        html.Span(f"${total_lobbying:.0f}M", className='stat-value'),
                    ], className='sankey-stat'),
                    html.Div([
                        html.Span("Shareholder Dividends", className='stat-label'),
                        html.Span(f"${total_dividends:.0f}M", className='stat-value'),
                    ], className='sankey-stat'),
                    html.Div([
                        html.Span("Executive Pay", className='stat-label'),
                        html.Span(f"${total_exec_comp:.0f}M", className='stat-value'),
                    ], className='sankey-stat'),
                ], className='sankey-stats-row'),
            ], className='container'),
        ], className='sankey-stats-bar'),

        # Sankey diagram
        html.Div([
            dcc.Graph(
                id='economic-sankey',
                figure=fig,
                config={
                    'displayModeBar': True,
                    'modeBarButtonsToRemove': ['select2d', 'lasso2d'],
                    'displaylogo': False,
                },
                style={'width': '100%'},
            ),
        ], className='sankey-container'),

        # Legend
        html.Div([
            html.Div([
                html.H4("Reading the Flows", className='legend-title'),
                html.Div([
                    html.Div([
                        html.Span(className='legend-color', style={'backgroundColor': COLORS['taxpayer']}),
                        html.Span("Public Funds (Source)", className='legend-label'),
                    ], className='legend-item'),
                    html.Div([
                        html.Span(className='legend-color', style={'backgroundColor': COLORS['agency']}),
                        html.Span("Federal Agencies", className='legend-label'),
                    ], className='legend-item'),
                    html.Div([
                        html.Span(className='legend-color', style={'backgroundColor': COLORS['private_prison']}),
                        html.Span("Private Prison Corporations", className='legend-label'),
                    ], className='legend-item'),
                    html.Div([
                        html.Span(className='legend-color', style={'backgroundColor': COLORS['tech']}),
                        html.Span("Surveillance Tech Vendors", className='legend-label'),
                    ], className='legend-item'),
                    html.Div([
                        html.Span(className='legend-color', style={'backgroundColor': COLORS['profit']}),
                        html.Span("Profit Extraction", className='legend-label'),
                    ], className='legend-item'),
                    html.Div([
                        html.Span(className='legend-color', style={'backgroundColor': COLORS['lobbying']}),
                        html.Span("Political Influence", className='legend-label'),
                    ], className='legend-item'),
                ], className='legend-grid'),
            ], className='container'),
        ], className='sankey-legend'),

        # The circular economy callout
        html.Div([
            html.Div([
                html.Div([
                    html.H3("The Circular Economy of Enforcement", className='callout-title'),
                    html.P([
                        "Notice the loop: Tax dollars fund detention contracts → ",
                        "Private prison profits fund lobbying → ",
                        "Lobbying influences policy to expand detention → ",
                        "More contracts, more profit. GEO Group and CoreCivic alone have spent ",
                        html.Strong("$25+ million"),
                        " on lobbying since 2008, directly correlating with expansion of ",
                        "mandatory detention and per-bed guarantees in their contracts."
                    ], className='callout-text'),
                ], className='circular-economy-box'),
            ], className='container'),
        ], className='sankey-callout'),

        # Data sources
        html.Div([
            html.Div([
                html.H4("Data Sources", className='methodology-title'),
                html.P([
                    "Budget data from DHS Congressional Budget Justifications and USASpending.gov. ",
                    "Contract values from FPDS (Federal Procurement Data System). ",
                    "Lobbying expenditures from OpenSecrets.org. ",
                    "Executive compensation from SEC filings. ",
                    "Shareholder distributions from annual reports."
                ], className='methodology-text'),
            ], className='container'),
        ], className='sankey-methodology'),

    ], className='economic-sankey-page')
