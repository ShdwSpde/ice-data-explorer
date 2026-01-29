"""
Project Watchtower - Deaths in Custody Infinite Memorial
FR 2.1: Humanizing data through individual stories

Visual Strategy: Infinite scroll of memorial cards, each representing
a life lost in ICE custody. Cards reveal on scroll with fade-in effect.
Dark, somber aesthetic with minimal color except for accent details.
"""

from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
from database import query_data


# Color palette for memorial
COLORS = {
    'bg': '#0a0a12',
    'card_bg': 'rgba(20, 20, 35, 0.8)',
    'text': '#e2e8f0',
    'text_muted': '#8d99ae',
    'accent': '#e53e3e',
    'border': 'rgba(255, 255, 255, 0.05)',
    'candle': '#ffd166',
}

# Known deaths in ICE custody with available details
# Sources: ACLU, Human Rights Watch, ICE FOIA releases, news reports
MEMORIAL_DATA = [
    {
        'name': 'Roxsana Hernández',
        'age': 33,
        'origin': 'Honduras',
        'date': 'May 25, 2018',
        'facility': 'Cibola County Correctional Center, NM',
        'cause': 'Complications from HIV, dehydration',
        'detained_days': 16,
        'story': 'Roxsana was a transgender woman who fled persecution in Honduras. She presented herself at a port of entry seeking asylum. Despite visible signs of illness, she was held in an ice box detention cell for days before being transferred. An independent autopsy revealed signs of abuse.',
        'source': 'ACLU, Transgender Law Center'
    },
    {
        'name': 'Jakelin Caal Maquín',
        'age': 7,
        'origin': 'Guatemala',
        'date': 'December 8, 2018',
        'facility': 'CBP Custody, Lordsburg, NM',
        'cause': 'Sepsis, dehydration',
        'detained_days': 2,
        'story': 'Jakelin and her father crossed the border seeking asylum. She developed a high fever while in custody but medical attention was delayed for hours. She died of septic shock at a hospital in El Paso.',
        'source': 'DHS OIG Report, CBS News'
    },
    {
        'name': 'Carlos Gregorio Hernandez Vasquez',
        'age': 16,
        'origin': 'Guatemala',
        'date': 'May 20, 2019',
        'facility': 'CBP Holding Facility, Weslaco, TX',
        'cause': 'Influenza complications',
        'detained_days': 6,
        'story': 'Carlos was diagnosed with the flu and a 103-degree fever but was not hospitalized. He was found unresponsive on the floor of his cell. Video showed he had been lying motionless for hours before anyone checked on him.',
        'source': 'ProPublica, DHS OIG'
    },
    {
        'name': 'Huy Chi Tran',
        'age': 47,
        'origin': 'Vietnam',
        'date': 'February 2019',
        'facility': 'Prairieland Detention Center, TX',
        'cause': 'Suicide',
        'detained_days': 180,
        'story': 'Huy was a legal permanent resident facing deportation after a criminal conviction. He had lived in the US for over 30 years. His family said he became increasingly despondent during his prolonged detention.',
        'source': 'RAICES, Houston Chronicle'
    },
    {
        'name': 'Johana Medina León',
        'age': 25,
        'origin': 'El Salvador',
        'date': 'June 1, 2019',
        'facility': 'Otero County Processing Center, NM',
        'cause': 'HIV complications, cardiac arrest',
        'detained_days': 4,
        'story': 'Johana was a transgender woman with HIV who sought asylum at a port of entry. Despite disclosing her medical condition, she did not receive adequate care. She died in a hospital days after being released from ICE custody.',
        'source': 'Diversidad Sin Fronteras, NBC News'
    },
    {
        'name': 'Fernando Dominguez',
        'age': 59,
        'origin': 'Mexico',
        'date': 'October 2019',
        'facility': 'Stewart Detention Center, GA',
        'cause': 'Heart attack, delayed care',
        'detained_days': 270,
        'story': 'Fernando had multiple chronic conditions including diabetes and heart disease. His family said he repeatedly complained about inadequate medical care. He suffered a fatal heart attack after months in detention.',
        'source': 'Project South, Atlanta Journal-Constitution'
    },
    {
        'name': 'Nebane Abienwi',
        'age': 37,
        'origin': 'Cameroon',
        'date': 'October 2019',
        'facility': 'San Diego ICE Custody',
        'cause': 'Brain hemorrhage',
        'detained_days': 14,
        'story': 'Nebane was an asylum seeker who fled political violence in Cameroon. He collapsed in detention and was rushed to a hospital where he died. His family believes his complaints of severe headaches were ignored.',
        'source': 'ACLU San Diego, Voice of San Diego'
    },
    {
        'name': 'Choung Woong Ahn',
        'age': 74,
        'origin': 'South Korea',
        'date': 'December 2019',
        'facility': 'Mesa Verde ICE Processing Center, CA',
        'cause': 'Complications from fall',
        'detained_days': 90,
        'story': 'Choung was the oldest person to die in ICE custody. He was a legal permanent resident detained for a decades-old conviction. He fell and suffered a brain bleed but was not immediately taken to a hospital.',
        'source': 'San Francisco Chronicle, CIVIC'
    },
    {
        'name': 'Carlos Escobar-Mejia',
        'age': 57,
        'origin': 'El Salvador',
        'date': 'May 2020',
        'facility': 'Otay Mesa Detention Center, CA',
        'cause': 'COVID-19',
        'detained_days': 45,
        'story': 'Carlos was the first person known to die of COVID-19 in ICE custody. He had been denied release despite the pandemic and his underlying health conditions. The facility had a major outbreak.',
        'source': 'LA Times, ACLU'
    },
    {
        'name': 'Santiago Baten-Oxlaj',
        'age': 34,
        'origin': 'Guatemala',
        'date': 'July 2020',
        'facility': 'Stewart Detention Center, GA',
        'cause': 'COVID-19 complications',
        'detained_days': 60,
        'story': 'Santiago died after a COVID-19 outbreak at Stewart Detention Center. He had underlying conditions that made him high-risk. Advocates had called for his release weeks before his death.',
        'source': 'El Refugio, Project South'
    },
    {
        'name': 'Onoval Perez-Montufa',
        'age': 51,
        'origin': 'Guatemala',
        'date': 'August 2020',
        'facility': 'Farmville Detention Center, VA',
        'cause': 'COVID-19',
        'detained_days': 120,
        'story': 'Onoval died during a massive COVID outbreak at Farmville that infected over 300 detainees. The facility had been cited for inadequate medical care. He leaves behind children in the US.',
        'source': 'ACLU Virginia, Washington Post'
    },
    {
        'name': 'Cipriano Chavez-Alvarez',
        'age': 61,
        'origin': 'Mexico',
        'date': 'September 2020',
        'facility': 'Eloy Detention Center, AZ',
        'cause': 'COVID-19',
        'detained_days': 90,
        'story': 'Cipriano died after contracting COVID-19 in detention. His family had been trying to secure his release for months. Eloy Detention Center has had one of the highest death rates of any ICE facility.',
        'source': 'ACLU Arizona, Arizona Republic'
    },
    {
        'name': 'Oscar Lopez Acosta',
        'age': 44,
        'origin': 'Mexico',
        'date': 'February 2021',
        'facility': 'Stewart Detention Center, GA',
        'cause': 'Hypertensive cardiovascular disease',
        'detained_days': 180,
        'story': 'Oscar had been in detention for six months when he died of heart disease. His family said he had been complaining of chest pains for weeks but was told it was anxiety. He leaves behind three children.',
        'source': 'Project South, Georgia Detention Watch'
    },
    {
        'name': 'Kesley Vial',
        'age': 45,
        'origin': 'Haiti',
        'date': 'March 2021',
        'facility': 'Torrance County Detention Facility, NM',
        'cause': 'Cardiac arrest, medical neglect',
        'detained_days': 60,
        'story': 'Kesley complained of chest pains for days before collapsing. Despite having a known heart condition, he was not given his prescribed medication. His death prompted calls for facility closure.',
        'source': 'ACLU New Mexico, NPR'
    },
    {
        'name': 'Unnamed Man',
        'age': 72,
        'origin': 'Unknown',
        'date': 'April 2023',
        'facility': 'ICE Custody (location withheld)',
        'cause': 'Undisclosed',
        'detained_days': 'Unknown',
        'story': 'ICE confirmed this death but has not released details including the person\'s name, nationality, or cause of death. Advocates continue to push for transparency in custody death reporting.',
        'source': 'ICE ERO Statistics'
    },
]


def create_memorial_card(person, index):
    """Create a single memorial card for a person who died in custody."""

    # Candle icon for visual element
    candle_svg = html.Div([
        html.Div(className='candle-flame'),
        html.Div(className='candle-body'),
    ], className='memorial-candle')

    return html.Div([
        # Left side: candle
        html.Div([
            candle_svg,
        ], className='memorial-card-candle'),

        # Right side: content
        html.Div([
            # Name and vital info
            html.Div([
                html.H3(
                    person['name'],
                    className='memorial-name'
                ),
                html.Div([
                    html.Span(f"Age {person['age']}", className='memorial-detail'),
                    html.Span(" | ", className='memorial-separator'),
                    html.Span(person['origin'], className='memorial-detail'),
                    html.Span(" | ", className='memorial-separator'),
                    html.Span(person['date'], className='memorial-detail memorial-date'),
                ], className='memorial-vitals'),
            ], className='memorial-header'),

            # Detention details
            html.Div([
                html.Div([
                    html.Span("Facility: ", className='detail-label'),
                    html.Span(person['facility'], className='detail-value'),
                ], className='memorial-facility'),
                html.Div([
                    html.Span("Cause of Death: ", className='detail-label'),
                    html.Span(person['cause'], className='detail-value cause-value'),
                ], className='memorial-cause'),
                html.Div([
                    html.Span("Days Detained: ", className='detail-label'),
                    html.Span(
                        str(person['detained_days']) if isinstance(person['detained_days'], int) else person['detained_days'],
                        className='detail-value'
                    ),
                ], className='memorial-days'),
            ], className='memorial-details'),

            # Story
            html.P(
                person['story'],
                className='memorial-story'
            ),

            # Source
            html.Div([
                html.Span("Source: ", className='source-label'),
                html.Span(person['source'], className='source-value'),
            ], className='memorial-source'),

        ], className='memorial-card-content'),

    ], className='memorial-card', style={'--card-index': index})


def get_memorial_content():
    """
    Build and return the Deaths in Custody Memorial page.

    Returns:
        Dash html.Div with infinite scroll memorial
    """
    # Calculate statistics
    total_deaths = len(MEMORIAL_DATA)
    avg_age = sum(p['age'] for p in MEMORIAL_DATA if isinstance(p['age'], int)) / len([p for p in MEMORIAL_DATA if isinstance(p['age'], int)])
    avg_detained = sum(p['detained_days'] for p in MEMORIAL_DATA if isinstance(p['detained_days'], int)) / len([p for p in MEMORIAL_DATA if isinstance(p['detained_days'], int)])

    # Countries represented
    countries = list(set(p['origin'] for p in MEMORIAL_DATA if p['origin'] != 'Unknown'))

    memorial_cards = [create_memorial_card(person, i) for i, person in enumerate(MEMORIAL_DATA)]

    return html.Div([
        # Header section
        html.Div([
            html.Div([
                html.H1([
                    "In Memoriam",
                ], className='memorial-title'),
                html.P([
                    "Lives lost in U.S. immigration detention. ",
                    "Each card represents a person—someone's child, parent, sibling, friend. ",
                    "Their deaths, documented here, demand accountability."
                ], className='memorial-subtitle'),
            ], className='container'),
        ], className='memorial-header-section'),

        # Statistics bar
        html.Div([
            html.Div([
                html.Div([
                    html.Div([
                        html.Span("Documented Deaths", className='stat-label'),
                        html.Span(f"{total_deaths}+", className='stat-value'),
                        html.Span("(2018-2024, partial)", className='stat-note'),
                    ], className='memorial-stat'),
                    html.Div([
                        html.Span("Average Age", className='stat-label'),
                        html.Span(f"{avg_age:.0f} years", className='stat-value'),
                    ], className='memorial-stat'),
                    html.Div([
                        html.Span("Avg. Time Detained", className='stat-label'),
                        html.Span(f"{avg_detained:.0f} days", className='stat-value'),
                    ], className='memorial-stat'),
                    html.Div([
                        html.Span("Countries", className='stat-label'),
                        html.Span(f"{len(countries)}", className='stat-value'),
                    ], className='memorial-stat'),
                ], className='memorial-stats-row'),
            ], className='container'),
        ], className='memorial-stats-bar'),

        # Important context
        html.Div([
            html.Div([
                html.Div([
                    html.Span("Important Context", className='context-label'),
                    html.P([
                        "These documented cases represent only a fraction of deaths in immigration detention. ",
                        "ICE's reporting has significant gaps: deaths that occur shortly after release, ",
                        "deaths in facilities with delayed reporting, and deaths where cause is disputed or undisclosed. ",
                        "Independent monitoring groups estimate the true count may be 2-3x higher than official figures."
                    ], className='context-text'),
                ], className='context-box'),
            ], className='container'),
        ], className='memorial-context-section'),

        # Memorial cards grid
        html.Div([
            html.Div(
                memorial_cards,
                className='memorial-grid',
                id='memorial-grid'
            ),
        ], className='memorial-cards-section'),

        # Call to action
        html.Div([
            html.Div([
                html.H3("Take Action", className='action-title'),
                html.P([
                    "These deaths were preventable. Inadequate medical care, overcrowding, ",
                    "COVID-19 neglect, and prolonged detention contributed to each one."
                ], className='action-text'),
                html.Div([
                    html.A(
                        "Support Detention Watch Network",
                        href="https://www.detentionwatchnetwork.org/",
                        target="_blank",
                        className='action-link'
                    ),
                    html.A(
                        "ACLU Immigrants' Rights Project",
                        href="https://www.aclu.org/issues/immigrants-rights",
                        target="_blank",
                        className='action-link'
                    ),
                    html.A(
                        "Freedom for Immigrants",
                        href="https://www.freedomforimmigrants.org/",
                        target="_blank",
                        className='action-link'
                    ),
                ], className='action-links'),
            ], className='container'),
        ], className='memorial-action-section'),

        # Methodology footer
        html.Div([
            html.Div([
                html.H4("Data Sources & Methodology", className='methodology-title'),
                html.P([
                    "Deaths documented through: ICE Enforcement and Removal Operations death reports, ",
                    "DHS Office of Inspector General investigations, ACLU FOIA requests, ",
                    "Human Rights Watch reports, news investigations, and advocacy organization tracking. ",
                    "Some details have been withheld by ICE citing privacy or pending investigations."
                ], className='methodology-text'),
            ], className='container'),
        ], className='memorial-methodology'),

    ], className='memorial-page')
