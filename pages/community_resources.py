"""
Community Resources - External ICE Tracking Tools & Databases
Curated links to public resources for community awareness and safety
"""

from dash import html, dcc
import dash_bootstrap_components as dbc


# Resource categories with links and descriptions
RESOURCES = {
    'tracking_tools': {
        'title': 'Real-Time Tracking & Reporting',
        'icon': '📍',
        'description': 'Community-powered tools for reporting and tracking ICE activity',
        'resources': [
            {
                'name': 'Documenting ICE',
                'url': 'https://documentingice.com',
                'description': 'Crowdsourced database tracking ICE vehicle sightings, including license plates, vehicle descriptions, and locations. Community members can report sightings.',
                'type': 'Vehicle Database',
                'maintained_by': 'Community volunteers'
            },
            {
                'name': 'ICE Raids Reporting (United We Dream)',
                'url': 'https://unitedwedream.org/protect',
                'description': 'Report ICE raids and enforcement activity in your community. Includes resources for documenting encounters.',
                'type': 'Raid Reporting',
                'maintained_by': 'United We Dream'
            },
            {
                'name': 'Mijente Notifica',
                'url': 'https://notifica.us',
                'description': 'Mobile app and platform for rapid community alerts about ICE activity. Create safety networks and receive notifications.',
                'type': 'Alert System',
                'maintained_by': 'Mijente'
            },
            {
                'name': 'RAICES ICE Watch',
                'url': 'https://www.raicestexas.org',
                'description': 'Texas-focused reporting and tracking of ICE enforcement activity with legal support resources.',
                'type': 'Regional Tracking',
                'maintained_by': 'RAICES Texas'
            },
        ]
    },
    'data_resources': {
        'title': 'Data & Research Databases',
        'icon': '📊',
        'description': 'Academic and investigative databases with ICE data',
        'resources': [
            {
                'name': 'TRAC Immigration',
                'url': 'https://trac.syr.edu/immigration/',
                'description': 'Syracuse University research center providing detailed ICE arrest, detention, and deportation statistics obtained via FOIA.',
                'type': 'Academic Database',
                'maintained_by': 'Syracuse University'
            },
            {
                'name': 'ICE Detention Facilities Map (CIVIC)',
                'url': 'https://www.freedomforimmigrants.org/map',
                'description': 'Interactive map of all ICE detention facilities with capacity, operator, and contact information.',
                'type': 'Facility Database',
                'maintained_by': 'Freedom for Immigrants'
            },
            {
                'name': 'Deportation Research',
                'url': 'https://deportationresearchclinic.org',
                'description': 'UC Davis research tracking deportation flights, destinations, and patterns.',
                'type': 'Flight Data',
                'maintained_by': 'UC Davis Law'
            },
            {
                'name': 'The Intercept - ICE Surveillance',
                'url': 'https://theintercept.com/series/ice-surveillance/',
                'description': 'Investigative journalism series on ICE surveillance technology, databases, and contractor relationships.',
                'type': 'Investigative',
                'maintained_by': 'The Intercept'
            },
            {
                'name': 'USASpending.gov - ICE Contracts',
                'url': 'https://www.usaspending.gov/search/?hash=3e8e47a8c9c16e8f47c6e52c0f6e1e5f',
                'description': 'Federal database of all ICE contract awards including private prison companies, tech vendors, and service providers.',
                'type': 'Contract Data',
                'maintained_by': 'US Treasury'
            },
            {
                'name': 'OpenSecrets - ICE Lobbying',
                'url': 'https://www.opensecrets.org/federal-lobbying/clients?cycle=2024&q=geo+group',
                'description': 'Track lobbying expenditures by private prison companies and immigration enforcement contractors.',
                'type': 'Lobbying Data',
                'maintained_by': 'OpenSecrets'
            },
        ]
    },
    'legal_resources': {
        'title': 'Legal Aid & Know Your Rights',
        'icon': '⚖️',
        'description': 'Legal assistance and rights information',
        'resources': [
            {
                'name': 'ACLU Know Your Rights',
                'url': 'https://www.aclu.org/know-your-rights/immigrants-rights',
                'description': 'Comprehensive guide to immigrant rights during encounters with ICE, at home, at work, and in public.',
                'type': 'Rights Guide',
                'maintained_by': 'ACLU'
            },
            {
                'name': 'National Immigration Law Center',
                'url': 'https://www.nilc.org',
                'description': 'Legal resources, policy analysis, and updates on immigration enforcement changes.',
                'type': 'Legal Resources',
                'maintained_by': 'NILC'
            },
            {
                'name': 'Immigration Advocates Network',
                'url': 'https://www.immigrationadvocates.org/nonprofit/legaldirectory/',
                'description': 'Directory of free and low-cost immigration legal services searchable by location.',
                'type': 'Legal Directory',
                'maintained_by': 'Pro Bono Net'
            },
            {
                'name': 'Immigrant Legal Resource Center',
                'url': 'https://www.ilrc.org',
                'description': 'Training, publications, and resources for immigration legal practitioners and advocates.',
                'type': 'Legal Training',
                'maintained_by': 'ILRC'
            },
            {
                'name': 'National Immigrant Justice Center',
                'url': 'https://immigrantjustice.org',
                'description': 'Direct legal services, policy advocacy, and detention monitoring in the Chicago area and nationally.',
                'type': 'Legal Services',
                'maintained_by': 'NIJC'
            },
        ]
    },
    'detention_monitoring': {
        'title': 'Detention Monitoring & Conditions',
        'icon': '🏢',
        'description': 'Resources for monitoring detention facilities and conditions',
        'resources': [
            {
                'name': 'Detention Watch Network',
                'url': 'https://www.detentionwatchnetwork.org',
                'description': 'National coalition tracking detention conditions, policy changes, and organizing for detention abolition.',
                'type': 'Advocacy Network',
                'maintained_by': 'DWN Coalition'
            },
            {
                'name': 'Human Rights Watch - US Immigration',
                'url': 'https://www.hrw.org/topic/immigration',
                'description': 'Investigations into detention conditions, abuse, and policy violations with reports and recommendations.',
                'type': 'Investigations',
                'maintained_by': 'Human Rights Watch'
            },
            {
                'name': 'ACLU Detention Facility Reports',
                'url': 'https://www.aclu.org/issues/immigrants-rights/ice-and-border-patrol-abuses',
                'description': 'Documentation of abuse, medical neglect, and constitutional violations in ICE custody.',
                'type': 'Abuse Documentation',
                'maintained_by': 'ACLU'
            },
            {
                'name': 'Project South - Georgia Detention',
                'url': 'https://projectsouth.org/ice-detention/',
                'description': 'Deep monitoring of Georgia detention facilities including Irwin County (site of medical abuse allegations).',
                'type': 'Regional Monitoring',
                'maintained_by': 'Project South'
            },
            {
                'name': 'Physicians for Human Rights',
                'url': 'https://phr.org/issues/asylum-and-immigration/',
                'description': 'Medical and forensic documentation of detention conditions and preventable deaths.',
                'type': 'Medical Documentation',
                'maintained_by': 'PHR'
            },
        ]
    },
    'community_defense': {
        'title': 'Community Defense & Rapid Response',
        'icon': '🤝',
        'description': 'Networks for community protection and rapid response',
        'resources': [
            {
                'name': 'Immigrant Defense Project',
                'url': 'https://www.immigrantdefenseproject.org',
                'description': 'Raid response training, know-your-rights workshops, and community defense resources.',
                'type': 'Defense Training',
                'maintained_by': 'IDP'
            },
            {
                'name': 'Make the Road New York',
                'url': 'https://maketheroadny.org',
                'description': 'Community organizing, legal services, and rapid response in New York with multilingual resources.',
                'type': 'Community Org',
                'maintained_by': 'MRNY'
            },
            {
                'name': 'CHIRLA (Coalition for Humane Immigrant Rights)',
                'url': 'https://www.chirla.org',
                'description': 'California-based advocacy with rapid response networks and community organizing.',
                'type': 'Regional Network',
                'maintained_by': 'CHIRLA'
            },
            {
                'name': 'Church World Service',
                'url': 'https://cwsglobal.org/take-action/immigration/',
                'description': 'Faith-based rapid response resources and sanctuary congregation support.',
                'type': 'Faith-Based',
                'maintained_by': 'CWS'
            },
        ]
    },
    'journalism': {
        'title': 'Investigative Journalism & News',
        'icon': '📰',
        'description': 'Ongoing investigative coverage of ICE operations',
        'resources': [
            {
                'name': 'The Marshall Project - Immigration',
                'url': 'https://www.themarshallproject.org/records/1309-immigration',
                'description': 'Nonprofit newsroom covering criminal justice including immigration enforcement and detention.',
                'type': 'Investigative News',
                'maintained_by': 'Marshall Project'
            },
            {
                'name': 'ProPublica - Immigration',
                'url': 'https://www.propublica.org/topics/immigration',
                'description': 'FOIA-powered investigations into ICE practices, deaths in custody, and enforcement patterns.',
                'type': 'Investigative News',
                'maintained_by': 'ProPublica'
            },
            {
                'name': 'BuzzFeed News - Immigration',
                'url': 'https://www.buzzfeednews.com/collection/immigration',
                'description': 'Breaking coverage of ICE operations, leaked documents, and detention conditions.',
                'type': 'News Coverage',
                'maintained_by': 'BuzzFeed News'
            },
            {
                'name': 'Border Chronicle',
                'url': 'https://www.theborderchronicle.com',
                'description': 'Newsletter focused exclusively on US-Mexico border enforcement and immigration policy.',
                'type': 'Newsletter',
                'maintained_by': 'Melissa del Bosque'
            },
            {
                'name': 'Documented NY',
                'url': 'https://documentedny.com',
                'description': 'New York-focused immigration news covering local enforcement and community impact.',
                'type': 'Local News',
                'maintained_by': 'Documented'
            },
        ]
    },
}


def get_community_resources_content():
    """Generate the community resources page content."""

    sections = []

    # Page header
    sections.append(
        html.Div([
            html.Div([
                html.H2("Community Resources & External Tools", className='section-title'),
                html.P([
                    "A curated collection of public resources for tracking ICE activity, ",
                    "understanding your rights, and connecting with community support networks. ",
                    html.Strong("These are external resources not maintained by this project.")
                ], className='section-intro'),
                html.Div([
                    html.Span("⚠️ ", style={'fontSize': '1.2rem'}),
                    html.Span(
                        "Always verify information and consult legal professionals for advice. "
                        "Links open in new tabs.",
                        style={'color': '#ffc107'}
                    )
                ], style={
                    'backgroundColor': 'rgba(255, 193, 7, 0.1)',
                    'padding': '12px 20px',
                    'borderRadius': '6px',
                    'marginTop': '20px',
                    'border': '1px solid rgba(255, 193, 7, 0.3)'
                })
            ], className='container'),
        ], style={'marginBottom': '30px'})
    )

    # Build each category section
    for category_key, category in RESOURCES.items():
        resource_cards = []

        for resource in category['resources']:
            resource_cards.append(
                html.Div([
                    html.Div([
                        html.Div([
                            html.H4([
                                html.A(
                                    resource['name'],
                                    href=resource['url'],
                                    target='_blank',
                                    style={'color': '#e94560', 'textDecoration': 'none'}
                                ),
                                html.Span(' ↗', style={'fontSize': '0.8rem', 'color': '#8d99ae'})
                            ], style={'marginBottom': '8px'}),
                            html.Span(
                                resource['type'],
                                style={
                                    'backgroundColor': 'rgba(233, 69, 96, 0.2)',
                                    'color': '#e94560',
                                    'padding': '2px 8px',
                                    'borderRadius': '4px',
                                    'fontSize': '0.75rem',
                                    'fontWeight': 'bold'
                                }
                            )
                        ], style={'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'flex-start', 'flexWrap': 'wrap', 'gap': '10px'}),
                        html.P(
                            resource['description'],
                            style={'color': '#b8c4ce', 'fontSize': '0.9rem', 'marginTop': '12px', 'marginBottom': '10px', 'lineHeight': '1.5'}
                        ),
                        html.Div([
                            html.Span("Maintained by: ", style={'color': '#8d99ae', 'fontSize': '0.8rem'}),
                            html.Span(resource['maintained_by'], style={'color': '#edf2f4', 'fontSize': '0.8rem', 'fontWeight': '500'})
                        ]),
                        html.A(
                            f"Visit {resource['name']} →",
                            href=resource['url'],
                            target='_blank',
                            style={
                                'display': 'inline-block',
                                'marginTop': '15px',
                                'color': '#e94560',
                                'textDecoration': 'none',
                                'fontSize': '0.85rem',
                                'fontWeight': '600',
                                'padding': '8px 16px',
                                'border': '1px solid #e94560',
                                'borderRadius': '4px',
                                'transition': 'all 0.2s ease'
                            },
                            className='resource-link-btn'
                        )
                    ], style={
                        'backgroundColor': 'rgba(22, 33, 62, 0.6)',
                        'padding': '20px',
                        'borderRadius': '8px',
                        'border': '1px solid #2b2d42',
                        'height': '100%'
                    })
                ], className='col-md-6 col-lg-4', style={'marginBottom': '20px'})
            )

        sections.append(
            html.Div([
                html.Div([
                    html.H3([
                        html.Span(category['icon'], style={'marginRight': '12px'}),
                        category['title']
                    ], style={'color': '#edf2f4', 'marginBottom': '10px'}),
                    html.P(category['description'], style={'color': '#8d99ae', 'marginBottom': '25px'}),
                    html.Div(resource_cards, className='row')
                ], className='container')
            ], style={
                'backgroundColor': 'rgba(15, 15, 35, 0.5)',
                'padding': '30px 0',
                'marginBottom': '20px',
                'borderTop': '1px solid #2b2d42',
                'borderBottom': '1px solid #2b2d42'
            })
        )

    # Disclaimer footer
    sections.append(
        html.Div([
            html.Div([
                html.Hr(style={'borderColor': '#2b2d42', 'margin': '30px 0'}),
                html.H4("Disclaimer", style={'color': '#8d99ae', 'marginBottom': '15px'}),
                html.P([
                    "This page provides links to external resources for informational purposes only. ",
                    "We do not control, endorse, or guarantee the accuracy of external content. ",
                    "Information may change without notice. Always verify current information directly with organizations. ",
                    "This is not legal advice—consult qualified immigration attorneys for legal guidance."
                ], style={'color': '#8d99ae', 'fontSize': '0.85rem', 'lineHeight': '1.6'}),
                html.P([
                    "Know of a resource that should be listed? ",
                    html.A(
                        "Submit a suggestion on GitHub",
                        href="https://github.com/ShdwSpde/ice-data-explorer/issues",
                        target="_blank",
                        style={'color': '#e94560'}
                    ),
                    "."
                ], style={'color': '#8d99ae', 'fontSize': '0.85rem', 'marginTop': '15px'})
            ], className='container')
        ], style={'marginTop': '20px', 'paddingBottom': '40px'})
    )

    return html.Div(sections, className='community-resources-page')
