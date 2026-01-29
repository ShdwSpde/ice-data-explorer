"""
Project Watchtower - Data Gap Submission System
FR 4.2: Allow users to report data discrepancies and gaps

Visual Strategy: Interactive form for reporting discrepancies between
official and observed data, with a feed showing submitted gaps
and their verification status.
"""

from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
from datetime import datetime


# Color palette
COLORS = {
    'bg': '#0f0f23',
    'card': 'rgba(22, 33, 62, 0.5)',
    'text': '#e2e8f0',
    'text_muted': '#8d99ae',
    'verified': '#06d6a0',
    'pending': '#ed8936',
    'disputed': '#e53e3e',
}

# Data gap categories
GAP_CATEGORIES = [
    {'value': 'deaths', 'label': 'Deaths in Custody'},
    {'value': 'medical', 'label': 'Medical Care Issues'},
    {'value': 'conditions', 'label': 'Facility Conditions'},
    {'value': 'statistics', 'label': 'Official Statistics Discrepancy'},
    {'value': 'contracts', 'label': 'Contract/Financial Data'},
    {'value': 'abuse', 'label': 'Abuse/Misconduct'},
    {'value': 'legal', 'label': 'Legal Violations'},
    {'value': 'other', 'label': 'Other'},
]

# Sample submitted gaps (in production, would be from database)
SAMPLE_SUBMISSIONS = [
    {
        'id': 'GAP-2024-0142',
        'category': 'deaths',
        'title': 'Unreported death at Adelanto',
        'summary': 'Local coroner records show death on Oct 15 not appearing in ICE reports',
        'official_claim': 'No deaths reported for October',
        'evidence': 'Coroner case #2024-1847',
        'submitted': '2024-01-10',
        'status': 'verified',
        'status_note': 'Confirmed via FOIA response',
    },
    {
        'id': 'GAP-2024-0138',
        'category': 'conditions',
        'title': 'Overcrowding at Stewart Detention',
        'summary': 'Facility operating at 147% capacity per fire marshal report',
        'official_claim': '95% occupancy reported to Congress',
        'evidence': 'Fire inspection report dated Nov 2023',
        'submitted': '2024-01-08',
        'status': 'pending',
        'status_note': 'Awaiting FOIA response',
    },
    {
        'id': 'GAP-2024-0125',
        'category': 'statistics',
        'title': 'Deportation flight count discrepancy',
        'summary': 'ICE Air flights tracked exceed official removal statistics by 23%',
        'official_claim': '142,580 removals in FY2024',
        'evidence': 'Flight tracking data from Witness at the Border',
        'submitted': '2024-01-05',
        'status': 'verified',
        'status_note': 'Difference attributed to "voluntary departures" not counted',
    },
    {
        'id': 'GAP-2024-0119',
        'category': 'medical',
        'title': 'Denied insulin medication',
        'summary': 'Family reports diabetic relative denied insulin for 5 days',
        'official_claim': 'All detainees receive medically necessary care',
        'evidence': 'Family testimony, attorney notes',
        'submitted': '2024-01-03',
        'status': 'pending',
        'status_note': 'Investigation ongoing',
    },
    {
        'id': 'GAP-2024-0112',
        'category': 'contracts',
        'title': 'Undisclosed GEO Group modification',
        'summary': '$45M contract modification not appearing in USASpending',
        'official_claim': 'All modifications publicly reported',
        'evidence': 'FPDS record vs USASpending comparison',
        'submitted': '2023-12-28',
        'status': 'disputed',
        'status_note': 'DHS claims reporting delay',
    },
]


def create_submission_card(submission):
    """Create a card for a submitted data gap."""
    status_colors = {
        'verified': COLORS['verified'],
        'pending': COLORS['pending'],
        'disputed': COLORS['disputed'],
    }

    status_icons = {
        'verified': '✓',
        'pending': '⏳',
        'disputed': '⚠️',
    }

    category_labels = {c['value']: c['label'] for c in GAP_CATEGORIES}

    return html.Div([
        # Header
        html.Div([
            html.Span(submission['id'], className='gap-id'),
            html.Span([
                html.Span(
                    status_icons[submission['status']],
                    className='status-icon'
                ),
                html.Span(
                    submission['status'].title(),
                    className='status-label',
                    style={'color': status_colors[submission['status']]}
                ),
            ], className='gap-status'),
        ], className='gap-header'),

        # Title and category
        html.H4(submission['title'], className='gap-title'),
        html.Span(
            category_labels.get(submission['category'], 'Other'),
            className='gap-category'
        ),

        # Summary
        html.P(submission['summary'], className='gap-summary'),

        # Official vs reported
        html.Div([
            html.Div([
                html.Span("Official Claim: ", className='claim-label'),
                html.Span(submission['official_claim'], className='claim-value official'),
            ], className='claim-row'),
            html.Div([
                html.Span("Evidence: ", className='claim-label'),
                html.Span(submission['evidence'], className='claim-value evidence'),
            ], className='claim-row'),
        ], className='gap-claims'),

        # Footer
        html.Div([
            html.Span(f"Submitted: {submission['submitted']}", className='gap-date'),
            html.Span(submission['status_note'], className='gap-note'),
        ], className='gap-footer'),

    ], className='gap-card', style={'--status-color': status_colors[submission['status']]})


def get_data_gaps_content():
    """
    Build and return the Data Gap Submission page.

    Returns:
        Dash html.Div with the submission system
    """
    submission_cards = [
        create_submission_card(sub) for sub in SAMPLE_SUBMISSIONS
    ]

    # Statistics
    verified_count = len([s for s in SAMPLE_SUBMISSIONS if s['status'] == 'verified'])
    pending_count = len([s for s in SAMPLE_SUBMISSIONS if s['status'] == 'pending'])
    disputed_count = len([s for s in SAMPLE_SUBMISSIONS if s['status'] == 'disputed'])

    return html.Div([
        # Header
        html.Div([
            html.Div([
                html.H2("Report a Data Gap", className='section-title'),
                html.P([
                    "Official government data often conflicts with on-the-ground reality. ",
                    "Help us document discrepancies by submitting evidence of data gaps—",
                    "unreported deaths, contradicted statistics, hidden contract modifications, ",
                    "and conditions that don't match official reports."
                ], className='section-intro'),
            ], className='container'),
        ], className='gaps-header'),

        # Statistics bar
        html.Div([
            html.Div([
                html.Div([
                    html.Div([
                        html.Span("Total Submissions", className='stat-label'),
                        html.Span(f"{len(SAMPLE_SUBMISSIONS)}", className='stat-value'),
                    ], className='gaps-stat'),
                    html.Div([
                        html.Span("Verified", className='stat-label'),
                        html.Span(f"{verified_count}", className='stat-value',
                                 style={'color': COLORS['verified']}),
                    ], className='gaps-stat'),
                    html.Div([
                        html.Span("Pending Review", className='stat-label'),
                        html.Span(f"{pending_count}", className='stat-value',
                                 style={'color': COLORS['pending']}),
                    ], className='gaps-stat'),
                    html.Div([
                        html.Span("Disputed", className='stat-label'),
                        html.Span(f"{disputed_count}", className='stat-value',
                                 style={'color': COLORS['disputed']}),
                    ], className='gaps-stat'),
                ], className='gaps-stats-row'),
            ], className='container'),
        ], className='gaps-stats-bar'),

        # Two-column layout: form + submissions
        html.Div([
            html.Div([
                # Submission form
                html.Div([
                    html.H3("Submit a Data Gap", className='subsection-title'),

                    html.Div([
                        html.Label("Category", className='form-label'),
                        dcc.Dropdown(
                            id='gap-category',
                            options=GAP_CATEGORIES,
                            placeholder='Select category...',
                            className='gap-dropdown',
                        ),
                    ], className='form-group'),

                    html.Div([
                        html.Label("Title", className='form-label'),
                        dcc.Input(
                            id='gap-title',
                            type='text',
                            placeholder='Brief title describing the gap',
                            className='gap-input',
                        ),
                    ], className='form-group'),

                    html.Div([
                        html.Label("What the official data says", className='form-label'),
                        dcc.Textarea(
                            id='gap-official',
                            placeholder='Quote or describe the official claim...',
                            className='gap-textarea',
                        ),
                    ], className='form-group'),

                    html.Div([
                        html.Label("What your evidence shows", className='form-label'),
                        dcc.Textarea(
                            id='gap-evidence',
                            placeholder='Describe the discrepancy and your evidence...',
                            className='gap-textarea',
                        ),
                    ], className='form-group'),

                    html.Div([
                        html.Label("Evidence source/documentation", className='form-label'),
                        dcc.Input(
                            id='gap-source',
                            type='text',
                            placeholder='FOIA reference, court filing, news report, etc.',
                            className='gap-input',
                        ),
                    ], className='form-group'),

                    html.Div([
                        html.Label("Your email (optional, for follow-up)", className='form-label'),
                        dcc.Input(
                            id='gap-email',
                            type='email',
                            placeholder='email@example.com',
                            className='gap-input',
                        ),
                    ], className='form-group'),

                    html.Button(
                        "Submit Data Gap",
                        id='submit-gap-btn',
                        className='submit-btn',
                    ),

                    html.Div(id='gap-submission-result', className='submission-result'),

                ], className='submission-form'),

                # Submissions feed
                html.Div([
                    html.H3("Recent Submissions", className='subsection-title'),
                    html.Div(submission_cards, className='submissions-feed'),
                ], className='submissions-section'),

            ], className='gaps-grid container'),
        ], className='gaps-content'),

        # Verification process
        html.Div([
            html.Div([
                html.H3("How Verification Works", className='subsection-title'),
                html.Div([
                    html.Div([
                        html.Div("1", className='step-number'),
                        html.H4("Submission", className='step-title'),
                        html.P("You submit evidence of a data discrepancy with documentation.",
                              className='step-text'),
                    ], className='verification-step'),
                    html.Div([
                        html.Div("2", className='step-number'),
                        html.H4("Review", className='step-title'),
                        html.P("Our team reviews the submission and requests additional FOIA documents if needed.",
                              className='step-text'),
                    ], className='verification-step'),
                    html.Div([
                        html.Div("3", className='step-number'),
                        html.H4("Verification", className='step-title'),
                        html.P("If confirmed, the gap is marked verified and incorporated into our analysis.",
                              className='step-text'),
                    ], className='verification-step'),
                    html.Div([
                        html.Div("4", className='step-number'),
                        html.H4("Transparency", className='step-title'),
                        html.P("All submissions (verified, pending, disputed) are published with methodology notes.",
                              className='step-text'),
                    ], className='verification-step'),
                ], className='verification-steps'),
            ], className='container'),
        ], className='verification-section'),

        # Privacy notice
        html.Div([
            html.Div([
                html.H4("Privacy & Security", className='privacy-title'),
                html.P([
                    "Submissions can be made anonymously. If you provide an email, it will only be used ",
                    "for follow-up questions about your submission. We use secure, encrypted storage ",
                    "and never share personal information with government agencies. If you're concerned ",
                    "about retaliation, consider using a VPN and anonymous email service."
                ], className='privacy-text'),
            ], className='container'),
        ], className='privacy-section'),

    ], className='data-gaps-page')
