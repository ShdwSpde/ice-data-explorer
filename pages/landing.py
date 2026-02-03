"""
Project Watchtower - Landing Page with Redaction Reveal
PAGE 1: Entry point with dramatic redaction reveal effect

Visual Strategy: Official-looking government document with heavy redactions.
On user interaction, redactions lift to reveal hidden truths underneath.
Sets the tone for the entire investigative experience.
"""

from dash import html, dcc, callback, Input, Output, State, clientside_callback
import dash_bootstrap_components as dbc


# The "document" content with redactions
# Format: (visible_text, redacted_truth)
DOCUMENT_SECTIONS = [
    {
        'type': 'header',
        'content': 'DEPARTMENT OF HOMELAND SECURITY',
        'subheader': 'Immigration and Customs Enforcement',
    },
    {
        'type': 'classification',
        'content': 'FOR OFFICIAL USE ONLY',
    },
    {
        'type': 'title',
        'content': 'Annual Performance Summary FY2024',
    },
    {
        'type': 'paragraph',
        'visible': 'ICE Enforcement and Removal Operations (ERO) continues to execute its mission of ',
        'redacted': 'separating families and terrorizing immigrant communities',
        'replacement': 'protecting public safety',
        'continue': ' through targeted enforcement actions.',
    },
    {
        'type': 'paragraph',
        'visible': 'In FY2024, ERO conducted ',
        'redacted': 'workplace raids that devastated local economies and left US citizen children without parents',
        'replacement': '[REDACTED - b(7)(E)]',
        'continue': ' operations across all 50 states.',
    },
    {
        'type': 'statistic',
        'label': 'Total Removals',
        'official': '142,580',
        'truth': '+ 89,000 "voluntary departures" coerced under threat',
        'note': 'Official statistics exclude pressured self-deportations',
    },
    {
        'type': 'statistic',
        'label': 'Average Detention Stay',
        'official': '34 days',
        'truth': 'Many held 6+ months without trial',
        'note': 'Median masks extreme outliers in prolonged detention',
    },
    {
        'type': 'statistic',
        'label': 'Detention Facility Inspections',
        'official': '98% compliance rate',
        'truth': 'Inspections are announced in advance; facilities clean up',
        'note': 'Self-reported metrics with no independent verification',
    },
    {
        'type': 'paragraph',
        'visible': 'ICE maintains ',
        'redacted': 'contracts guaranteeing private prisons minimum occupancy regardless of need, costing taxpayers $billions',
        'replacement': '[REDACTED - b(4)]',
        'continue': ' partnership agreements with detention facility operators.',
    },
    {
        'type': 'paragraph',
        'visible': 'The use of ',
        'redacted': 'solitary confinement for weeks or months, often as retaliation for complaints',
        'replacement': 'administrative segregation',
        'continue': ' follows established protocols.',
    },
    {
        'type': 'callout',
        'visible': 'DEATHS IN CUSTODY: ',
        'official': '21',
        'truth': '45+ when including deaths shortly after release from medical neglect',
        'note': 'ICE only counts deaths while physically in custody',
    },
    {
        'type': 'paragraph',
        'visible': 'Medical care is provided by ',
        'redacted': 'the lowest bidder, with documented cases of untreated cancer, denied insulin, and ignored heart attacks',
        'replacement': 'qualified healthcare professionals',
        'continue': ' at all facilities.',
    },
    {
        'type': 'footer',
        'content': 'This document contains sensitive information. Unauthorized disclosure may result in civil and criminal penalties.',
        'truth': 'The real crime is what this document hides.',
    },
]


def create_redacted_span(text, is_redacted=True, redaction_id=None):
    """Create a span element with redaction styling."""
    if is_redacted:
        return html.Span([
            html.Span(text, className='redacted-truth', id=f'truth-{redaction_id}'),
            html.Span(
                '█' * min(len(text) // 2, 30),
                className='redaction-bar',
                id=f'bar-{redaction_id}'
            ),
        ], className='redacted-container')
    return html.Span(text)


def create_document_section(section, index):
    """Create a document section based on type."""
    section_type = section['type']

    if section_type == 'header':
        return html.Div([
            html.Div(section['content'], className='doc-header'),
            html.Div(section['subheader'], className='doc-subheader'),
            html.Div(className='doc-seal'),  # Government seal placeholder
        ], className='doc-header-section')

    elif section_type == 'classification':
        return html.Div(
            section['content'],
            className='doc-classification'
        )

    elif section_type == 'title':
        return html.H1(section['content'], className='doc-title')

    elif section_type == 'paragraph':
        return html.P([
            html.Span(section['visible']),
            html.Span([
                html.Span(section['redacted'], className='redacted-truth'),
                html.Span(section['replacement'], className='redaction-bar official-text'),
            ], className='redacted-container', **{'data-index': str(index)}),
            html.Span(section['continue']),
        ], className='doc-paragraph')

    elif section_type == 'statistic':
        return html.Div([
            html.Div(section['label'], className='stat-label'),
            html.Div([
                html.Span([
                    html.Span(section['truth'], className='redacted-truth stat-truth'),
                    html.Span(section['official'], className='redaction-bar stat-official'),
                ], className='redacted-container stat-container', **{'data-index': str(index)}),
            ], className='stat-value-row'),
            html.Div(section['note'], className='stat-note hidden-note'),
        ], className='doc-statistic')

    elif section_type == 'callout':
        return html.Div([
            html.Span(section['visible'], className='callout-label'),
            html.Span([
                html.Span(section['truth'], className='redacted-truth'),
                html.Span(section['official'], className='redaction-bar'),
            ], className='redacted-container', **{'data-index': str(index)}),
            html.Div(section['note'], className='callout-note hidden-note'),
        ], className='doc-callout')

    elif section_type == 'footer':
        return html.Div([
            html.Div(section['content'], className='doc-footer-official'),
            html.Div(section['truth'], className='doc-footer-truth'),
        ], className='doc-footer')

    return html.Div()


def get_landing_content():
    """
    Build and return the Landing Page with Redaction Reveal.

    Returns:
        Dash html.Div with the full landing experience
    """
    document_sections = [
        create_document_section(section, i)
        for i, section in enumerate(DOCUMENT_SECTIONS)
    ]

    return html.Div([
        # Intro overlay (shown first)
        html.Div([
            html.Div([
                html.H1("The Cost of Enforcement", className='landing-title'),
                html.P([
                    "What the government tells you about immigration enforcement ",
                    "isn't the whole story. Official reports are sanitized, statistics ",
                    "cherry-picked, and uncomfortable truths redacted."
                ], className='landing-intro'),
                html.P([
                    "This is an investigative data tool. It combines official government data ",
                    "with independent sources to reveal what's hidden between the lines."
                ], className='landing-intro'),
                html.Button(
                    "Reveal the Truth",
                    id='begin-reveal-btn',
                    className='reveal-button pulse'
                ),
                html.Div([
                    html.Span("Scroll to explore", className='scroll-hint'),
                    html.Div(className='scroll-indicator'),
                ], className='scroll-prompt'),
            ], className='intro-content'),
        ], className='landing-intro-overlay', id='intro-overlay'),

        # The "document"
        html.Div([
            html.Div([
                html.Div(
                    document_sections,
                    className='gov-document',
                    id='gov-document'
                ),

                # Reveal controls
                html.Div([
                    html.Button(
                        "Lift All Redactions",
                        id='lift-redactions-btn',
                        className='lift-button'
                    ),
                    html.Div([
                        html.Span("Or hover over ", className='hover-hint'),
                        html.Span("black bars", className='hover-hint-bar'),
                        html.Span(" to reveal individually", className='hover-hint'),
                    ], className='hover-instructions'),
                ], className='reveal-controls'),

            ], className='document-container'),
        ], className='document-section', id='document-section'),

        # Call to action / navigation
        html.Div([
            html.Div([
                html.H2("Explore the Data", className='explore-title'),
                html.P([
                    "This is just the beginning. Dive deeper into the data behind ",
                    "immigration enforcement—detention conditions, deportation patterns, ",
                    "corporate profits, and human costs."
                ], className='explore-intro'),

                html.Div([
                    html.A([
                        html.Div("📊", className='nav-card-icon'),
                        html.H3("Statistics Dashboard", className='nav-card-title'),
                        html.P("Official vs. independent data comparison", className='nav-card-desc'),
                    ], href='#', className='nav-card', **{'data-tab': 'tab-dashboard'}),

                    html.A([
                        html.Div("🗺️", className='nav-card-icon'),
                        html.H3("Detention Network", className='nav-card-title'),
                        html.P("Map the geography of incarceration", className='nav-card-desc'),
                    ], href='#', className='nav-card', **{'data-tab': 'tab-narratives'}),

                    html.A([
                        html.Div("💰", className='nav-card-icon'),
                        html.H3("Follow the Money", className='nav-card-title'),
                        html.P("Who profits from enforcement", className='nav-card-desc'),
                    ], href='#', className='nav-card', **{'data-tab': 'tab-budget'}),

                    html.A([
                        html.Div("🕯️", className='nav-card-icon'),
                        html.H3("Memorial", className='nav-card-title'),
                        html.P("Honoring lives lost in custody", className='nav-card-desc'),
                    ], href='#', className='nav-card', **{'data-tab': 'tab-narratives'}),
                ], className='nav-cards-grid'),

            ], className='container'),
        ], className='explore-section'),

        # Methodology note
        html.Div([
            html.Div([
                html.H4("About This Project", className='about-title'),
                html.P([
                    "Project Watchtower combines data from DHS, ICE, CBP, TRAC Immigration, ",
                    "ACLU, Human Rights Watch, and investigative journalism to provide a more ",
                    "complete picture of U.S. immigration enforcement. When official and independent ",
                    "sources disagree, we show both—because transparency means showing the full range ",
                    "of what's known, not just what's convenient."
                ], className='about-text'),
            ], className='container'),
        ], className='about-section'),

    ], className='landing-page', id='landing-page')


# Clientside callback for redaction reveal effect
REVEAL_JS = """
function(n_clicks) {
    if (n_clicks) {
        // Show document section
        const docSection = document.getElementById('document-section');
        if (docSection) {
            docSection.classList.add('visible');
        }
        // Return new className for intro-overlay
        return 'landing-intro-overlay hidden';
    }
    return 'landing-intro-overlay';
}
"""

LIFT_ALL_JS = """
function(n_clicks) {
    if (n_clicks) {
        // Show all hidden notes
        const doc = document.getElementById('gov-document');
        if (doc) {
            const notes = doc.querySelectorAll('.hidden-note');
            notes.forEach(note => note.classList.add('visible'));
        }
        // Return new className for gov-document
        return 'gov-document revealed';
    }
    return 'gov-document';
}
"""
