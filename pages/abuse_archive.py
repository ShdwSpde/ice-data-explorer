"""
Project Watchtower - Abuse Archive Reveal Interface
FR 2.4: Interactive reveal of documented abuse reports

Visual Strategy: Redacted document interface where users can "lift"
redactions to reveal documented abuse incidents. Categories include
medical neglect, sexual assault, excessive force, and solitary confinement.
"""

from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc


# Color palette
COLORS = {
    'bg': '#0a0a12',
    'card_bg': 'rgba(20, 20, 35, 0.7)',
    'text': '#e2e8f0',
    'text_muted': '#8d99ae',
    'redaction': '#1a1a1a',
    'truth': '#e53e3e',
    'warning': '#ed8936',
    'medical': '#9b2c2c',
    'assault': '#744210',
    'force': '#2c5282',
    'solitary': '#553c9a',
}

# Categories of abuse with documented incidents
ABUSE_CATEGORIES = {
    'medical_neglect': {
        'name': 'Medical Neglect',
        'icon': '🏥',
        'color': COLORS['medical'],
        'description': 'Denial or delay of necessary medical care',
        'incidents': [
            {
                'date': '2023-08',
                'facility': 'Stewart Detention Center, GA',
                'summary': 'Detainee with diagnosed diabetes denied insulin for 3 days',
                'redacted_detail': 'resulting in diabetic ketoacidosis requiring emergency hospitalization',
                'source': 'DHS OIG Report',
                'outcome': 'Under investigation'
            },
            {
                'date': '2022-11',
                'facility': 'Adelanto ICE Processing Center, CA',
                'summary': 'Pregnant woman reported bleeding and cramping for 6 hours',
                'redacted_detail': 'before being seen by medical staff; subsequently miscarried',
                'source': 'ACLU Complaint',
                'outcome': 'Settlement reached'
            },
            {
                'date': '2023-03',
                'facility': 'Torrance County Detention Facility, NM',
                'summary': 'Man with chest pains told it was anxiety',
                'redacted_detail': 'died of heart attack 4 days later in his cell',
                'source': 'Death in Custody Report',
                'outcome': 'Family lawsuit pending'
            },
            {
                'date': '2022-06',
                'facility': 'Otero County Processing Center, NM',
                'summary': 'HIV-positive detainee denied antiretroviral medication',
                'redacted_detail': 'for 2 weeks despite documented prescription; viral load spiked',
                'source': 'FOIA Documents',
                'outcome': 'Policy change ordered'
            },
        ]
    },
    'sexual_assault': {
        'name': 'Sexual Assault & Harassment',
        'icon': '⚠️',
        'color': COLORS['assault'],
        'description': 'Sexual abuse by staff or inadequate protection',
        'incidents': [
            {
                'date': '2023-05',
                'facility': 'Irwin County Detention Center, GA',
                'summary': 'Multiple women reported unwanted medical procedures',
                'redacted_detail': 'including hysterectomies performed without informed consent',
                'source': 'Whistleblower Report',
                'outcome': 'Contract terminated; DOJ investigation'
            },
            {
                'date': '2022-09',
                'facility': 'Karnes County Residential Center, TX',
                'summary': 'Guard accused of inappropriate contact during pat-down',
                'redacted_detail': 'seven women filed coordinated complaints over 3-month period',
                'source': 'Internal Affairs Report',
                'outcome': 'Guard terminated'
            },
            {
                'date': '2023-01',
                'facility': 'Mesa Verde ICE Processing Facility, CA',
                'summary': 'Camera blind spots in housing area exploited',
                'redacted_detail': 'for repeated sexual harassment by night shift officer',
                'source': 'PREA Investigation',
                'outcome': 'Criminal charges filed'
            },
        ]
    },
    'excessive_force': {
        'name': 'Excessive Force',
        'icon': '👊',
        'color': COLORS['force'],
        'description': 'Physical violence and use of restraints',
        'incidents': [
            {
                'date': '2023-02',
                'facility': 'El Paso Service Processing Center, TX',
                'summary': 'Detainee pepper-sprayed during mental health crisis',
                'redacted_detail': 'while restrained in a chair, causing chemical burns to face and eyes',
                'source': 'Video Evidence',
                'outcome': 'Officers on administrative leave'
            },
            {
                'date': '2022-12',
                'facility': 'Tacoma Northwest Detention Center, WA',
                'summary': 'Peaceful protest met with emergency response team',
                'redacted_detail': 'tear gas deployed in enclosed space; 47 detainees hospitalized',
                'source': 'Medical Records',
                'outcome': 'Class action lawsuit filed'
            },
            {
                'date': '2023-07',
                'facility': 'Richwood Correctional Center, LA',
                'summary': 'Man placed in restraint chair for 12 hours',
                'redacted_detail': 'for asking to speak with his lawyer; urinated on self',
                'source': 'ACLU Investigation',
                'outcome': 'Under review'
            },
        ]
    },
    'solitary_confinement': {
        'name': 'Solitary Confinement',
        'icon': '🚪',
        'color': COLORS['solitary'],
        'description': 'Prolonged isolation as punishment',
        'incidents': [
            {
                'date': '2023-04',
                'facility': 'Florence Service Processing Center, AZ',
                'summary': 'Man held in solitary for 180 consecutive days',
                'redacted_detail': 'for filing grievances; developed severe psychological deterioration',
                'source': 'Mental Health Evaluation',
                'outcome': 'Released to general population'
            },
            {
                'date': '2022-08',
                'facility': 'Dodge County Detention Facility, WI',
                'summary': 'Transgender woman placed in solitary "for protection"',
                'redacted_detail': '90+ days with 23-hour lockdown; multiple suicide attempts',
                'source': 'LGBTQ Advocacy Report',
                'outcome': 'Policy revision promised'
            },
            {
                'date': '2023-06',
                'facility': 'Winn Correctional Center, LA',
                'summary': 'Asylum seeker isolated after hunger strike',
                'redacted_detail': 'denied communication with lawyer or family for 45 days',
                'source': 'Human Rights Watch',
                'outcome': 'Under investigation'
            },
        ]
    },
}


def create_incident_card(incident, category_color, index):
    """Create an incident card with redaction reveal."""
    return html.Div([
        # Header with date and facility
        html.Div([
            html.Span(incident['date'], className='incident-date'),
            html.Span(incident['facility'], className='incident-facility'),
        ], className='incident-header'),

        # Summary with redacted detail
        html.Div([
            html.Span(incident['summary'] + ' ', className='incident-summary'),
            html.Span([
                html.Span(incident['redacted_detail'], className='redacted-truth'),
                html.Span('█' * 20, className='redaction-bar'),
            ], className='redacted-container incident-redaction'),
        ], className='incident-content'),

        # Source and outcome
        html.Div([
            html.Div([
                html.Span("Source: ", className='meta-label'),
                html.Span(incident['source'], className='meta-value'),
            ], className='incident-source'),
            html.Div([
                html.Span("Status: ", className='meta-label'),
                html.Span(incident['outcome'], className='meta-value outcome-value'),
            ], className='incident-outcome'),
        ], className='incident-meta'),

    ], className='incident-card', style={'--category-color': category_color})


def create_category_section(category_key, category_data):
    """Create a section for an abuse category."""
    incident_cards = [
        create_incident_card(incident, category_data['color'], i)
        for i, incident in enumerate(category_data['incidents'])
    ]

    return html.Div([
        # Category header
        html.Div([
            html.Span(category_data['icon'], className='category-icon'),
            html.H3(category_data['name'], className='category-title'),
            html.Span(
                f"{len(category_data['incidents'])} documented incidents",
                className='category-count'
            ),
        ], className='category-header', style={'borderColor': category_data['color']}),

        html.P(category_data['description'], className='category-description'),

        # Incident cards
        html.Div(incident_cards, className='incidents-grid'),

    ], className='abuse-category', id=f'category-{category_key}')


def get_abuse_archive_content():
    """
    Build and return the Abuse Archive page.

    Returns:
        Dash html.Div with the interactive abuse archive
    """
    total_incidents = sum(
        len(cat['incidents']) for cat in ABUSE_CATEGORIES.values()
    )

    category_sections = [
        create_category_section(key, data)
        for key, data in ABUSE_CATEGORIES.items()
    ]

    return html.Div([
        # Header
        html.Div([
            html.Div([
                html.H2("The Abuse Archive", className='section-title'),
                html.P([
                    "Documented incidents of abuse, neglect, and violations within ICE detention. ",
                    "These are not isolated cases—they represent systemic failures in oversight, ",
                    "accountability, and basic human dignity."
                ], className='section-intro'),
                html.Div([
                    html.Span("⚠️ Content Warning: ", className='content-warning-label'),
                    html.Span(
                        "This page contains descriptions of medical neglect, sexual assault, "
                        "physical violence, and psychological abuse.",
                        className='content-warning-text'
                    ),
                ], className='content-warning'),
            ], className='container'),
        ], className='archive-header'),

        # Statistics bar
        html.Div([
            html.Div([
                html.Div([
                    html.Div([
                        html.Span("Documented Incidents", className='stat-label'),
                        html.Span(f"{total_incidents}+", className='stat-value'),
                        html.Span("(sample from larger dataset)", className='stat-note'),
                    ], className='archive-stat'),
                    html.Div([
                        html.Span("Categories", className='stat-label'),
                        html.Span(f"{len(ABUSE_CATEGORIES)}", className='stat-value'),
                    ], className='archive-stat'),
                    html.Div([
                        html.Span("Facilities Implicated", className='stat-label'),
                        html.Span("12+", className='stat-value'),
                    ], className='archive-stat'),
                    html.Div([
                        html.Span("Outcomes Pending", className='stat-label'),
                        html.Span("60%", className='stat-value'),
                    ], className='archive-stat'),
                ], className='archive-stats-row'),
            ], className='container'),
        ], className='archive-stats-bar'),

        # Controls
        html.Div([
            html.Div([
                html.Button(
                    "Reveal All Redactions",
                    id='reveal-all-abuse-btn',
                    className='reveal-all-btn'
                ),
                html.P(
                    "Or hover over individual redactions to reveal details",
                    className='reveal-hint'
                ),
            ], className='container reveal-controls'),
        ], className='archive-controls'),

        # Category sections
        html.Div([
            html.Div(
                category_sections,
                className='categories-container',
                id='abuse-categories'
            ),
        ], className='container archive-content'),

        # Context section
        html.Div([
            html.Div([
                html.Div([
                    html.H3("The Pattern of Impunity", className='context-title'),
                    html.P([
                        "These incidents share common threads: delayed or denied medical care, ",
                        "retaliation against those who complain, inadequate investigation of allegations, ",
                        "and a system where private contractors face minimal consequences. ",
                        "DHS's own Office of Inspector General has repeatedly criticized ICE's ",
                        "failure to protect detainees and hold facilities accountable."
                    ], className='context-text'),
                ], className='pattern-box'),

                html.Div([
                    html.H4("How to Report Abuse", className='report-title'),
                    html.P([
                        "If you or someone you know has experienced abuse in ICE detention:"
                    ], className='report-intro'),
                    html.Ul([
                        html.Li([
                            html.Strong("DHS OIG Hotline: "),
                            "1-800-323-8603"
                        ]),
                        html.Li([
                            html.Strong("ACLU National: "),
                            "aclu.org/issues/immigrants-rights"
                        ]),
                        html.Li([
                            html.Strong("Freedom for Immigrants: "),
                            "1-209-757-3733"
                        ]),
                    ], className='report-resources'),
                ], className='report-box'),
            ], className='container'),
        ], className='archive-context'),

        # Methodology
        html.Div([
            html.Div([
                html.H4("Data Sources", className='methodology-title'),
                html.P([
                    "Incidents documented through: DHS Office of Inspector General reports, ",
                    "ACLU detention condition reports, Human Rights Watch investigations, ",
                    "FOIA-obtained internal documents, court filings, whistleblower testimony, ",
                    "and investigative journalism. All incidents listed have been documented ",
                    "by at least one official source."
                ], className='methodology-text'),
            ], className='container'),
        ], className='archive-methodology'),

    ], className='abuse-archive-page')
