"""
Project Watchtower - Taxpayer Receipt
PAGE 17: Personal Tax Calculator with Receipt Visualization

Visual Strategy: Interactive Digital Receipt
Makes the abstract personal by showing exactly where your tax dollars go.
"""

from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc


# Budget breakdown data (2025 figures in billions)
BUDGET_BREAKDOWN = {
    'ICE Enforcement & Removal': 4.8,
    'ICE Detention Operations': 3.4,
    'Border Patrol Operations': 7.3,
    'CBP Processing & Surveillance': 5.2,
    'Immigration Courts': 1.1,
    'ICE Air Operations (Flights)': 0.8,
    'Private Prison Contracts': 2.1,
    'Surveillance Technology': 1.5,
    'Wall Construction/Maintenance': 2.8,
    'Administrative & Other': 1.0,
}

TOTAL_BUDGET = 170  # $170 billion total
FEDERAL_BUDGET = 6800  # Total federal discretionary spending (approx)

# Opportunity cost multipliers (from academic sources)
OPPORTUNITY_COSTS = {
    'teacher_salary': {
        'amount': 65000,
        'label': 'Teacher salaries (annual)',
        'source': 'Bureau of Labor Statistics'
    },
    'pell_grants': {
        'amount': 7395,
        'label': 'Pell Grants (full award)',
        'source': 'Federal Student Aid'
    },
    'school_lunches': {
        'amount': 3.75,
        'label': 'Free school lunches',
        'source': 'USDA National School Lunch Program'
    },
    'affordable_housing': {
        'amount': 15000,
        'label': 'Annual housing vouchers',
        'source': 'HUD Section 8 average'
    },
    'healthcare_visits': {
        'amount': 250,
        'label': 'Primary care visits',
        'source': 'KFF Healthcare Cost Study'
    },
    'infrastructure_repairs': {
        'amount': 50000,
        'label': 'Pothole repairs',
        'source': 'ASCE Infrastructure Report'
    },
    'mental_health': {
        'amount': 150,
        'label': 'Mental health sessions',
        'source': 'SAMHSA Treatment Costs'
    },
    'childcare_months': {
        'amount': 1230,
        'label': 'Months of childcare',
        'source': 'Child Care Aware of America'
    }
}


def calculate_tax_contribution(income, filing_status='single'):
    """
    Calculate estimated federal tax and ICE portion.
    Uses simplified 2024 tax brackets.
    """
    # Simplified effective tax rates by income
    if income <= 11600:
        effective_rate = 0.10
    elif income <= 47150:
        effective_rate = 0.12
    elif income <= 100525:
        effective_rate = 0.15
    elif income <= 191950:
        effective_rate = 0.18
    elif income <= 243725:
        effective_rate = 0.22
    elif income <= 609350:
        effective_rate = 0.26
    else:
        effective_rate = 0.30

    # Adjust for filing status
    if filing_status == 'married':
        effective_rate *= 0.85  # Slightly lower effective rate
    elif filing_status == 'hoh':
        effective_rate *= 0.90

    federal_tax = income * effective_rate

    # ICE portion = (ICE budget / Federal budget) * your federal tax
    ice_percentage = (TOTAL_BUDGET / FEDERAL_BUDGET)
    ice_contribution = federal_tax * ice_percentage

    return {
        'federal_tax': federal_tax,
        'ice_contribution': ice_contribution,
        'ice_percentage': ice_percentage * 100
    }


def generate_receipt_items(ice_contribution):
    """Generate itemized receipt based on budget proportions."""
    items = []
    total_check = 0

    for category, amount_billions in BUDGET_BREAKDOWN.items():
        proportion = amount_billions / TOTAL_BUDGET
        your_share = ice_contribution * proportion
        items.append({
            'category': category,
            'amount': your_share,
            'budget_billions': amount_billions
        })
        total_check += your_share

    return items


def get_taxpayer_receipt_content():
    """
    Main content for the Taxpayer Receipt page.
    """
    return html.Div([
        # Header
        html.Div([
            html.H2("Your Personal ICE Receipt", className='section-title'),
            html.P([
                "The $170 billion immigration enforcement budget comes from your taxes. ",
                "See exactly where your money goes."
            ], className='section-intro'),
        ], className='container'),

        # Calculator Input
        html.Div([
            html.Div([
                html.Div([
                    html.Label("Annual Income", className='input-label'),
                    dcc.Input(
                        id='receipt-income',
                        type='number',
                        value=60000,
                        min=0,
                        max=10000000,
                        step=1000,
                        className='receipt-input'
                    ),
                ], className='input-group'),

                html.Div([
                    html.Label("Filing Status", className='input-label'),
                    dcc.Dropdown(
                        id='receipt-status',
                        options=[
                            {'label': 'Single', 'value': 'single'},
                            {'label': 'Married Filing Jointly', 'value': 'married'},
                            {'label': 'Head of Household', 'value': 'hoh'},
                        ],
                        value='single',
                        clearable=False,
                        className='receipt-dropdown'
                    ),
                ], className='input-group'),

                html.Button(
                    "GENERATE RECEIPT",
                    id='generate-receipt-btn',
                    className='btn-receipt'
                ),
            ], className='receipt-form')
        ], className='container form-section'),

        # Receipt Output
        html.Div(id='taxpayer-receipt-output', className='receipt-output-container'),

        # Opportunity Cost Section
        html.Div([
            html.H3("What Else Could Your Money Fund?", className='opportunity-title'),
            html.Div(id='opportunity-cost-output', className='opportunity-grid'),
        ], className='container opportunity-section'),

        # Context
        html.Div([
            html.Div([
                html.H4("Understanding These Numbers", className='context-title'),
                html.Div([
                    html.Div([
                        html.Div("$170B", className='context-stat'),
                        html.Div("Total ICE/CBP Budget", className='context-label'),
                    ], className='context-item'),
                    html.Div([
                        html.Div("2.5%", className='context-stat'),
                        html.Div("of Federal Spending", className='context-label'),
                    ], className='context-item'),
                    html.Div([
                        html.Div("$70,236", className='context-stat'),
                        html.Div("Cost per Deportation", className='context-label'),
                    ], className='context-item'),
                ], className='context-stats-row'),
                html.P([
                    "This is more than the combined budgets of the ",
                    html.Strong("Department of Education, EPA, NASA, and NSF"),
                    "."
                ], className='context-comparison'),
            ], className='context-card')
        ], className='container'),

    ], className='taxpayer-receipt-page')


def generate_receipt_html(income, filing_status):
    """Generate the visual receipt HTML."""
    calc = calculate_tax_contribution(income, filing_status)
    items = generate_receipt_items(calc['ice_contribution'])

    # Receipt header
    receipt_items = [
        html.Div([
            html.Div("═" * 40, className='receipt-border'),
            html.Div("TAXPAYER RECEIPT", className='receipt-header'),
            html.Div("U.S. Immigration Enforcement", className='receipt-subheader'),
            html.Div("═" * 40, className='receipt-border'),
        ], className='receipt-top'),

        html.Div([
            html.Div([
                html.Span("Annual Income:", className='receipt-field'),
                html.Span(f"${income:,.0f}", className='receipt-value'),
            ], className='receipt-row'),
            html.Div([
                html.Span("Est. Federal Tax:", className='receipt-field'),
                html.Span(f"${calc['federal_tax']:,.0f}", className='receipt-value'),
            ], className='receipt-row'),
            html.Div([
                html.Span("ICE/CBP Portion:", className='receipt-field'),
                html.Span(f"{calc['ice_percentage']:.1f}%", className='receipt-value'),
            ], className='receipt-row'),
        ], className='receipt-summary'),

        html.Div("─" * 40, className='receipt-divider'),
        html.Div("ITEMIZED BREAKDOWN", className='receipt-section-title'),
        html.Div("─" * 40, className='receipt-divider'),
    ]

    # Add itemized lines
    for item in items:
        category_short = item['category'][:30]
        receipt_items.append(
            html.Div([
                html.Span(category_short, className='receipt-item-name'),
                html.Span(f"${item['amount']:.2f}", className='receipt-item-amount'),
            ], className='receipt-item-row')
        )

    # Receipt total
    receipt_items.extend([
        html.Div("═" * 40, className='receipt-border'),
        html.Div([
            html.Span("YOUR ICE CONTRIBUTION:", className='receipt-total-label'),
            html.Span(f"${calc['ice_contribution']:.2f}", className='receipt-total-amount'),
        ], className='receipt-total'),
        html.Div("═" * 40, className='receipt-border'),

        html.Div([
            html.Div("Thank you for your contribution to", className='receipt-footer-line'),
            html.Div("immigration enforcement.", className='receipt-footer-line'),
            html.Div("* * * * *", className='receipt-footer-stars'),
        ], className='receipt-footer'),
    ])

    return html.Div(receipt_items, className='receipt-paper')


def generate_opportunity_costs(ice_contribution):
    """Generate opportunity cost comparisons."""
    items = []

    for key, data in OPPORTUNITY_COSTS.items():
        count = ice_contribution / data['amount']

        if count >= 1:
            display_count = f"{count:.1f}" if count < 10 else f"{int(count):,}"
        else:
            display_count = f"{count:.2f}"

        items.append(
            html.Div([
                html.Div(display_count, className='opportunity-count'),
                html.Div(data['label'], className='opportunity-label'),
                html.Div(f"Source: {data['source']}", className='opportunity-source'),
            ], className='opportunity-card')
        )

    return items
