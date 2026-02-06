"""
ICE Data Explorer - Database Setup and Data Seeding
Comprehensive immigration enforcement data from multiple sources

Supports both SQLite (development) and PostgreSQL (production).
Set DATABASE_URL environment variable for PostgreSQL, otherwise defaults to SQLite.
"""

import os
from datetime import datetime
from contextlib import contextmanager

# Database configuration
DATABASE_URL = os.environ.get('DATABASE_URL')
USE_POSTGRES = DATABASE_URL is not None and DATABASE_URL.startswith('postgres')

if USE_POSTGRES:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    # Handle Heroku-style postgres:// URLs
    if DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
else:
    import sqlite3

DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'ice_data.db')


def get_connection():
    """Get database connection based on environment."""
    if USE_POSTGRES:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    else:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row  # Enable dict-like access
        return conn


@contextmanager
def get_db_cursor(dict_cursor=False):
    """Context manager for database connections with automatic cleanup."""
    conn = get_connection()
    try:
        if USE_POSTGRES and dict_cursor:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
        else:
            cursor = conn.cursor()
        yield cursor
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()


def get_placeholder():
    """Return the appropriate placeholder for parameterized queries."""
    return '%s' if USE_POSTGRES else '?'


def adapt_query(query):
    """Adapt SQLite query syntax for PostgreSQL if needed."""
    if USE_POSTGRES:
        # Replace ? with %s for parameters
        query = query.replace('?', '%s')
        # Replace AUTOINCREMENT with SERIAL
        query = query.replace('INTEGER PRIMARY KEY AUTOINCREMENT', 'SERIAL PRIMARY KEY')
        # Replace TEXT with proper PostgreSQL types where beneficial
        # (TEXT works in both, but this allows for future optimization)
    return query


def execute_query(query, params=None, fetch=False, fetchone=False, dict_cursor=False):
    """Execute a query with automatic placeholder adaptation."""
    adapted_query = adapt_query(query)
    with get_db_cursor(dict_cursor=dict_cursor) as cursor:
        if params:
            cursor.execute(adapted_query, params)
        else:
            cursor.execute(adapted_query)

        if fetchone:
            return cursor.fetchone()
        elif fetch:
            return cursor.fetchall()
        return cursor.lastrowid if not USE_POSTGRES else None


def init_database():
    """Initialize database with all tables."""
    conn = get_connection()
    cursor = conn.cursor()

    # Helper to create table with PostgreSQL/SQLite compatibility
    def create_table(sql):
        cursor.execute(adapt_query(sql))

    # Budget/Funding Tables
    create_table('''
        CREATE TABLE IF NOT EXISTS agency_budgets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            year INTEGER NOT NULL,
            agency TEXT NOT NULL,
            budget_millions REAL NOT NULL,
            budget_adjusted_millions REAL,
            notes TEXT,
            source TEXT
        )
    ''')

    create_table('''
        CREATE TABLE IF NOT EXISTS budget_allocations_2025 (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            amount_billions REAL NOT NULL,
            description TEXT,
            source TEXT
        )
    ''')

    # Detention Tables
    create_table('''
        CREATE TABLE IF NOT EXISTS detention_population (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            year INTEGER NOT NULL,
            month INTEGER,
            population INTEGER NOT NULL,
            with_criminal_record INTEGER,
            without_criminal_record INTEGER,
            pending_charges INTEGER,
            source TEXT
        )
    ''')

    create_table('''
        CREATE TABLE IF NOT EXISTS detention_by_state (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            year INTEGER NOT NULL,
            state TEXT NOT NULL,
            population INTEGER NOT NULL,
            facilities_count INTEGER,
            source TEXT
        )
    ''')

    # Deportation Tables
    create_table('''
        CREATE TABLE IF NOT EXISTS deportations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fiscal_year INTEGER NOT NULL,
            removals INTEGER NOT NULL,
            returns INTEGER,
            total INTEGER,
            source TEXT
        )
    ''')

    create_table('''
        CREATE TABLE IF NOT EXISTS deportations_by_nationality (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fiscal_year INTEGER NOT NULL,
            nationality TEXT NOT NULL,
            count INTEGER NOT NULL,
            percentage REAL,
            source TEXT
        )
    ''')

    # Deaths and Abuse Tables
    create_table('''
        CREATE TABLE IF NOT EXISTS deaths_in_custody (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            year INTEGER NOT NULL,
            deaths INTEGER NOT NULL,
            preventable_percentage REAL,
            notes TEXT,
            source TEXT
        )
    ''')

    create_table('''
        CREATE TABLE IF NOT EXISTS abuse_complaints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            year INTEGER NOT NULL,
            category TEXT NOT NULL,
            count INTEGER,
            description TEXT,
            source TEXT
        )
    ''')

    # Cost Tables
    create_table('''
        CREATE TABLE IF NOT EXISTS deportation_costs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cost_type TEXT NOT NULL,
            amount_dollars REAL NOT NULL,
            source TEXT,
            notes TEXT
        )
    ''')

    create_table('''
        CREATE TABLE IF NOT EXISTS private_prison_contracts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            year INTEGER NOT NULL,
            company TEXT NOT NULL,
            revenue_millions REAL NOT NULL,
            source TEXT
        )
    ''')

    # Staffing
    create_table('''
        CREATE TABLE IF NOT EXISTS staffing (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            year INTEGER NOT NULL,
            agency TEXT NOT NULL,
            employees INTEGER NOT NULL,
            source TEXT
        )
    ''')

    # Arrests
    create_table('''
        CREATE TABLE IF NOT EXISTS arrests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            year INTEGER NOT NULL,
            month INTEGER,
            arrests INTEGER NOT NULL,
            daily_average REAL,
            source TEXT
        )
    ''')

    create_table('''
        CREATE TABLE IF NOT EXISTS arrests_by_state (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            year INTEGER NOT NULL,
            state TEXT NOT NULL,
            arrests_per_100k REAL NOT NULL,
            total_arrests INTEGER,
            source TEXT
        )
    ''')

    # Criminal Records Analysis
    create_table('''
        CREATE TABLE IF NOT EXISTS detainee_criminal_status (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            year INTEGER NOT NULL,
            no_convictions_pct REAL,
            violent_convictions_pct REAL,
            nonviolent_convictions_pct REAL,
            pending_charges_pct REAL,
            source TEXT
        )
    ''')

    # Key Statistics / Highlights
    create_table('''
        CREATE TABLE IF NOT EXISTS key_statistics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            metric TEXT NOT NULL,
            value TEXT NOT NULL,
            context TEXT,
            year INTEGER,
            source TEXT,
            impact_score INTEGER
        )
    ''')

    # News Articles / Headlines Timeline
    create_table('''
        CREATE TABLE IF NOT EXISTS news_articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            headline TEXT NOT NULL,
            source TEXT NOT NULL,
            url TEXT,
            category TEXT,
            sentiment_score REAL,
            sentiment_label TEXT,
            summary TEXT,
            image_url TEXT
        )
    ''')

    # Detention Facilities (for Facility Deep-Dive)
    create_table('''
        CREATE TABLE IF NOT EXISTS detention_facilities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            city TEXT,
            state TEXT NOT NULL,
            lat REAL,
            lon REAL,
            operator TEXT,
            facility_type TEXT,
            capacity INTEGER,
            current_population INTEGER,
            deaths_total INTEGER DEFAULT 0,
            complaints_total INTEGER DEFAULT 0,
            per_diem_rate REAL,
            annual_contract_value REAL,
            inspection_score TEXT,
            last_inspection_date TEXT,
            opened_date TEXT,
            notes TEXT
        )
    ''')

    # Legislative Tracker
    create_table('''
        CREATE TABLE IF NOT EXISTS legislation (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bill_number TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            status TEXT,
            introduced_date TEXT,
            last_action_date TEXT,
            sponsor TEXT,
            party TEXT,
            category TEXT,
            funding_amount REAL,
            vote_house TEXT,
            vote_senate TEXT,
            impact_summary TEXT
        )
    ''')

    # Translations for multi-language support
    create_table('''
        CREATE TABLE IF NOT EXISTS translations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT NOT NULL,
            lang TEXT NOT NULL,
            value TEXT NOT NULL,
            UNIQUE(key, lang)
        )
    ''')

    # Data freshness tracking (legacy - kept for compatibility)
    create_table('''
        CREATE TABLE IF NOT EXISTS data_sources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_name TEXT NOT NULL,
            last_updated TEXT,
            update_frequency TEXT,
            url TEXT,
            status TEXT DEFAULT 'active'
        )
    ''')

    # ========================================
    # DATA TRANSPARENCY TABLES
    # ========================================

    # Detailed source registry with trust levels
    create_table('''
        CREATE TABLE IF NOT EXISTS source_registry (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_name TEXT NOT NULL UNIQUE,
            source_type TEXT CHECK(source_type IN ('government', 'ngo', 'academic', 'media', 'legal', 'investigative')),
            trust_level TEXT CHECK(trust_level IN ('high', 'medium', 'low', 'contested')),
            organization_type TEXT,
            political_lean TEXT,
            funding_notes TEXT,
            methodology_notes TEXT,
            url TEXT,
            archive_url TEXT,
            last_verified DATE,
            verification_notes TEXT,
            known_limitations TEXT,
            recommended_use TEXT
        )
    ''')

    # Data points with full provenance
    create_table('''
        CREATE TABLE IF NOT EXISTS data_provenance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            metric_name TEXT NOT NULL,
            metric_category TEXT,
            display_value TEXT NOT NULL,
            numeric_value REAL,
            unit TEXT,
            date_period TEXT,
            date_retrieved DATE,
            primary_source_id INTEGER REFERENCES source_registry(id),
            verification_status TEXT CHECK(verification_status IN ('verified', 'unverified', 'contested', 'government_only', 'retracted')),
            government_figure TEXT,
            independent_figure TEXT,
            recommended_figure TEXT,
            discrepancy_explanation TEXT,
            cross_references TEXT,
            methodology_url TEXT,
            caveats TEXT,
            last_verified DATE
        )
    ''')

    # Source contradictions tracker
    create_table('''
        CREATE TABLE IF NOT EXISTS source_contradictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            metric_name TEXT NOT NULL,
            metric_category TEXT,
            government_source TEXT,
            government_value TEXT,
            government_methodology TEXT,
            independent_source TEXT,
            independent_value TEXT,
            independent_methodology TEXT,
            discrepancy_reason TEXT,
            recommended_value TEXT,
            recommendation_rationale TEXT,
            severity TEXT CHECK(severity IN ('minor', 'significant', 'major', 'critical')),
            date_identified DATE,
            notes TEXT
        )
    ''')

    # ========================================
    # INDUSTRIAL COMPLEX TABLES
    # For economic critique & corporate tracking
    # ========================================

    # Federal contracts from USASpending.gov
    create_table('''
        CREATE TABLE IF NOT EXISTS federal_contracts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contract_id TEXT UNIQUE,
            award_id TEXT,
            piid TEXT,
            award_type TEXT,
            award_description TEXT,
            naics_code TEXT,
            naics_description TEXT,
            awarding_agency TEXT,
            awarding_sub_agency TEXT,
            recipient_name TEXT,
            recipient_uei TEXT,
            recipient_parent_name TEXT,
            recipient_address TEXT,
            recipient_city TEXT,
            recipient_state TEXT,
            recipient_zip TEXT,
            total_obligation REAL,
            base_and_all_options_value REAL,
            current_total_value REAL,
            potential_total_value REAL,
            period_of_performance_start DATE,
            period_of_performance_end DATE,
            award_date DATE,
            last_modified_date DATE,
            extent_competed TEXT,
            solicitation_procedures TEXT,
            type_of_contract_pricing TEXT,
            contract_bundling TEXT,
            multi_year_contract TEXT,
            place_of_performance_city TEXT,
            place_of_performance_state TEXT,
            place_of_performance_zip TEXT,
            is_sole_source INTEGER DEFAULT 0,
            is_no_bid INTEGER DEFAULT 0,
            raw_data TEXT,
            date_ingested DATE DEFAULT CURRENT_DATE
        )
    ''')

    # Contract amendments and modifications
    create_table('''
        CREATE TABLE IF NOT EXISTS contract_modifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contract_id TEXT REFERENCES federal_contracts(contract_id),
            modification_number TEXT,
            modification_reason TEXT,
            action_type TEXT,
            action_date DATE,
            obligation_change REAL,
            new_total_value REAL,
            description TEXT,
            date_ingested DATE DEFAULT CURRENT_DATE
        )
    ''')

    # Corporate contractors (GEO Group, CoreCivic, etc.)
    create_table('''
        CREATE TABLE IF NOT EXISTS corporate_contractors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            uei TEXT UNIQUE,
            name TEXT NOT NULL,
            parent_company TEXT,
            ticker_symbol TEXT,
            company_type TEXT,
            headquarters_city TEXT,
            headquarters_state TEXT,
            total_ice_contracts REAL,
            total_dhs_contracts REAL,
            total_federal_contracts REAL,
            annual_revenue REAL,
            ice_revenue_percentage REAL,
            employees INTEGER,
            lobbying_total REAL,
            political_contributions REAL,
            sec_cik TEXT,
            website TEXT,
            notes TEXT,
            last_updated DATE
        )
    ''')

    # Lobbying data from OpenSecrets
    create_table('''
        CREATE TABLE IF NOT EXISTS lobbying_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filing_id TEXT UNIQUE,
            registrant_name TEXT,
            registrant_id TEXT,
            client_name TEXT,
            client_id TEXT,
            filing_year INTEGER,
            filing_type TEXT,
            amount REAL,
            income REAL,
            expenses REAL,
            agencies_lobbied TEXT,
            specific_issues TEXT,
            lobbyists TEXT,
            is_immigration_related INTEGER DEFAULT 0,
            date_filed DATE,
            date_ingested DATE DEFAULT CURRENT_DATE
        )
    ''')

    # Campaign contributions
    create_table('''
        CREATE TABLE IF NOT EXISTS campaign_contributions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_id TEXT UNIQUE,
            contributor_name TEXT,
            contributor_type TEXT,
            recipient_name TEXT,
            recipient_id TEXT,
            recipient_party TEXT,
            recipient_office TEXT,
            recipient_state TEXT,
            amount REAL,
            contribution_date DATE,
            contribution_type TEXT,
            industry TEXT,
            is_pac INTEGER DEFAULT 0,
            cycle INTEGER,
            date_ingested DATE DEFAULT CURRENT_DATE
        )
    ''')

    # Revolving door personnel
    create_table('''
        CREATE TABLE IF NOT EXISTS revolving_door_personnel (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            person_name TEXT NOT NULL,
            position_title TEXT,
            organization TEXT NOT NULL,
            organization_type TEXT CHECK(organization_type IN ('government', 'contractor', 'lobbying', 'ngo', 'other')),
            start_date DATE,
            end_date DATE,
            is_current INTEGER DEFAULT 0,
            previous_position_id INTEGER REFERENCES revolving_door_personnel(id),
            salary_estimate REAL,
            source TEXT,
            linkedin_url TEXT,
            notes TEXT,
            date_verified DATE
        )
    ''')

    # Surveillance tech vendors
    create_table('''
        CREATE TABLE IF NOT EXISTS surveillance_vendors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name TEXT NOT NULL,
            parent_company TEXT,
            product_name TEXT,
            product_category TEXT CHECK(product_category IN (
                'facial_recognition', 'biometrics', 'location_tracking',
                'social_media_monitoring', 'data_brokering', 'communications_interception',
                'predictive_analytics', 'document_verification', 'license_plate_readers',
                'drone_surveillance', 'database_systems', 'other'
            )),
            capability_description TEXT,
            ice_contract_value REAL,
            cbp_contract_value REAL,
            other_dhs_value REAL,
            contract_start_date DATE,
            contract_end_date DATE,
            privacy_concerns TEXT,
            known_issues TEXT,
            source TEXT,
            last_updated DATE
        )
    ''')

    # Stock price tracking (for policy correlation)
    create_table('''
        CREATE TABLE IF NOT EXISTS stock_prices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT NOT NULL,
            company_name TEXT,
            date DATE NOT NULL,
            open_price REAL,
            high_price REAL,
            low_price REAL,
            close_price REAL,
            adjusted_close REAL,
            volume INTEGER,
            UNIQUE(ticker, date)
        )
    ''')

    # Policy events for correlation analysis
    create_table('''
        CREATE TABLE IF NOT EXISTS policy_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_date DATE NOT NULL,
            event_type TEXT,
            title TEXT NOT NULL,
            description TEXT,
            source TEXT,
            url TEXT,
            impact_category TEXT,
            stock_impact_observed INTEGER DEFAULT 0,
            notes TEXT
        )
    ''')

    # Deaths in custody - individual records for memorial
    create_table('''
        CREATE TABLE IF NOT EXISTS deaths_individual (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            name_known INTEGER DEFAULT 0,
            age INTEGER,
            gender TEXT,
            nationality TEXT,
            date_of_death DATE,
            facility_name TEXT,
            facility_id INTEGER REFERENCES detention_facilities(id),
            cause_of_death TEXT,
            cause_category TEXT,
            was_preventable INTEGER,
            days_in_custody INTEGER,
            medical_care_concerns TEXT,
            official_report_url TEXT,
            independent_investigation_url TEXT,
            autopsy_available INTEGER DEFAULT 0,
            lawsuit_filed INTEGER DEFAULT 0,
            media_coverage_urls TEXT,
            source TEXT,
            verification_status TEXT,
            notes TEXT
        )
    ''')

    # Error reports from users
    create_table('''
        CREATE TABLE IF NOT EXISTS error_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            error_type TEXT NOT NULL,
            metric_name TEXT,
            description TEXT NOT NULL,
            suggested_source_url TEXT,
            reporter_email TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'new'
        )
    ''')

    # Data changelog for transparency
    create_table('''
        CREATE TABLE IF NOT EXISTS data_changelog (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            change_date DATE NOT NULL,
            change_type TEXT NOT NULL,
            category TEXT,
            metric_name TEXT,
            old_value TEXT,
            new_value TEXT,
            reason TEXT,
            source_url TEXT,
            verified_by TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # FOIA request tracking
    create_table('''
        CREATE TABLE IF NOT EXISTS foia_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            request_date DATE NOT NULL,
            agency TEXT NOT NULL,
            description TEXT NOT NULL,
            data_requested TEXT,
            status TEXT DEFAULT 'pending',
            response_date DATE,
            response_summary TEXT,
            documents_received INTEGER DEFAULT 0,
            appeal_filed INTEGER DEFAULT 0,
            source_url TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()
    print(f"Database initialized successfully. Using {'PostgreSQL' if USE_POSTGRES else 'SQLite'}.")


def seed_data():
    """Seed database with comprehensive ICE data."""
    conn = get_connection()
    cursor = conn.cursor()

    # Clear existing data
    tables = [
        'agency_budgets', 'budget_allocations_2025', 'detention_population',
        'detention_by_state', 'deportations', 'deportations_by_nationality',
        'deaths_in_custody', 'abuse_complaints', 'deportation_costs',
        'private_prison_contracts', 'staffing', 'arrests', 'arrests_by_state',
        'detainee_criminal_status', 'key_statistics', 'news_articles',
        'detention_facilities', 'legislation', 'translations', 'data_sources',
        'source_registry', 'data_provenance', 'source_contradictions'
    ]
    for table in tables:
        cursor.execute(f'DELETE FROM {table}')

    # ========================================
    # AGENCY BUDGETS - Historical Data
    # ========================================

    # Border Patrol Budget (1994-2024)
    border_patrol_budgets = [
        (1994, 'Border Patrol', 400, 820, 'Baseline year', 'American Immigration Council'),
        (1996, 'Border Patrol', 600, 1165, None, 'American Immigration Council'),
        (1998, 'Border Patrol', 877, 1640, None, 'American Immigration Council'),
        (2000, 'Border Patrol', 1055, 1868, None, 'American Immigration Council'),
        (2002, 'Border Patrol', 1416, 2398, None, 'American Immigration Council'),
        (2003, 'Border Patrol', 1500, 2485, 'DHS created', 'American Immigration Council'),
        (2004, 'Border Patrol', 1800, 2907, None, 'American Immigration Council'),
        (2006, 'Border Patrol', 2300, 3480, None, 'American Immigration Council'),
        (2008, 'Border Patrol', 2900, 4107, None, 'American Immigration Council'),
        (2010, 'Border Patrol', 3500, 4894, None, 'American Immigration Council'),
        (2012, 'Border Patrol', 3800, 5040, None, 'American Immigration Council'),
        (2014, 'Border Patrol', 3900, 5012, None, 'American Immigration Council'),
        (2016, 'Border Patrol', 4200, 5282, None, 'American Immigration Council'),
        (2018, 'Border Patrol', 4700, 5649, None, 'American Immigration Council'),
        (2020, 'Border Patrol', 5000, 5880, None, 'American Immigration Council'),
        (2022, 'Border Patrol', 6100, 6466, None, 'American Immigration Council'),
        (2024, 'Border Patrol', 7300, 7300, 'Current', 'American Immigration Council'),
    ]

    # ICE Budget (2003-2025)
    ice_budgets = [
        (2003, 'ICE', 3300, 5471, 'Agency founding', 'American Immigration Council'),
        (2004, 'ICE', 3700, 5976, None, 'American Immigration Council'),
        (2006, 'ICE', 4200, 6354, None, 'American Immigration Council'),
        (2008, 'ICE', 5000, 7080, None, 'American Immigration Council'),
        (2010, 'ICE', 5700, 7973, None, 'American Immigration Council'),
        (2012, 'ICE', 5900, 7824, None, 'American Immigration Council'),
        (2014, 'ICE', 5900, 7582, None, 'American Immigration Council'),
        (2016, 'ICE', 6200, 7799, None, 'American Immigration Council'),
        (2018, 'ICE', 7100, 8535, None, 'American Immigration Council'),
        (2019, 'ICE', 7600, 8837, 'Pre-pandemic', 'American Immigration Council'),
        (2020, 'ICE', 8000, 9408, None, 'American Immigration Council'),
        (2021, 'ICE', 8300, 9296, None, 'American Immigration Council'),
        (2022, 'ICE', 8800, 9328, None, 'American Immigration Council'),
        (2023, 'ICE', 9200, 9384, None, 'American Immigration Council'),
        (2024, 'ICE', 9600, 9600, None, 'American Immigration Council'),
        (2025, 'ICE', 75000, 75000, 'Big Beautiful Bill - unprecedented increase', 'American Immigration Council'),
    ]

    # CBP Budget (2003-2024)
    cbp_budgets = [
        (2003, 'CBP', 5900, 9781, 'DHS created', 'American Immigration Council'),
        (2006, 'CBP', 8000, 12103, None, 'American Immigration Council'),
        (2010, 'CBP', 11300, 15804, None, 'American Immigration Council'),
        (2014, 'CBP', 12400, 15937, None, 'American Immigration Council'),
        (2018, 'CBP', 15100, 18152, None, 'American Immigration Council'),
        (2020, 'CBP', 17000, 19992, None, 'American Immigration Council'),
        (2022, 'CBP', 18300, 19402, None, 'American Immigration Council'),
        (2024, 'CBP', 19600, 19600, None, 'American Immigration Council'),
    ]

    for data in border_patrol_budgets + ice_budgets + cbp_budgets:
        cursor.execute('''
            INSERT INTO agency_budgets (year, agency, budget_millions, budget_adjusted_millions, notes, source)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', data)

    # ========================================
    # 2025 BUDGET ALLOCATIONS
    # ========================================
    allocations_2025 = [
        ('Detention Centers', 45, 'Building new immigration detention centers including family facilities - 265% increase', 'American Immigration Council'),
        ('Enforcement & Deportation', 29.9, 'ICE enforcement and removal operations - 3x annual budget', 'American Immigration Council'),
        ('Border Infrastructure', 46, 'Border wall and physical infrastructure', 'Brennan Center'),
        ('Technology & Surveillance', 15, 'Border surveillance technology and systems', 'Brennan Center'),
        ('Personnel & Operations', 34.1, 'Additional staffing and operational costs', 'American Immigration Council'),
    ]

    for data in allocations_2025:
        cursor.execute('''
            INSERT INTO budget_allocations_2025 (category, amount_billions, description, source)
            VALUES (?, ?, ?, ?)
        ''', data)

    # ========================================
    # DETENTION POPULATION
    # ========================================
    detention_pop = [
        ('2014-10-01', 2014, 10, 33400, None, None, None, 'ICE Statistics'),
        ('2015-10-01', 2015, 10, 31000, None, None, None, 'ICE Statistics'),
        ('2016-10-01', 2016, 10, 35000, None, None, None, 'ICE Statistics'),
        ('2017-10-01', 2017, 10, 38000, None, None, None, 'ICE Statistics'),
        ('2018-10-01', 2018, 10, 44600, None, None, None, 'ICE Statistics'),
        ('2019-09-01', 2019, 9, 52000, None, None, None, 'Migration Policy Institute'),
        ('2020-03-01', 2020, 3, 38000, None, None, None, 'ICE Statistics'),
        ('2021-01-01', 2021, 1, 15000, None, None, None, 'ICE Statistics'),
        ('2022-10-01', 2022, 10, 25000, None, None, None, 'ICE Statistics'),
        ('2023-06-01', 2023, 6, 28000, None, None, None, 'Freedom for Immigrants'),
        ('2024-01-01', 2024, 1, 35000, None, None, None, 'ICE Statistics'),
        ('2024-12-14', 2024, 12, 38500, None, None, None, 'Guardian'),
        ('2025-01-20', 2025, 1, 40000, None, None, None, 'CBS News'),
        ('2025-06-01', 2025, 6, 55000, None, 11700, None, 'American Immigration Council'),
        ('2025-09-01', 2025, 9, 62000, 15719, 16251, 14332, 'American Immigration Council'),
        ('2025-10-01', 2025, 10, 66000, None, None, None, 'Migration Policy Institute'),
        ('2025-12-14', 2025, 12, 68440, None, None, None, 'Guardian'),
        ('2026-01-15', 2026, 1, 73000, None, None, None, 'CBS News'),
    ]

    for data in detention_pop:
        cursor.execute('''
            INSERT INTO detention_population
            (date, year, month, population, with_criminal_record, without_criminal_record, pending_charges, source)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', data)

    # ========================================
    # DETENTION BY STATE (2023 and 2025)
    # ========================================
    detention_states = [
        (2023, 'Texas', 9657, 25, 'Freedom for Immigrants'),
        (2023, 'Louisiana', 4416, 12, 'Freedom for Immigrants'),
        (2023, 'California', 1793, 8, 'Freedom for Immigrants'),
        (2023, 'Georgia', 1593, 6, 'Freedom for Immigrants'),
        (2023, 'Arizona', 1592, 5, 'Freedom for Immigrants'),
        (2025, 'Texas', 18500, 30, 'Prison Policy Initiative'),
        (2025, 'Louisiana', 8200, 15, 'Prison Policy Initiative'),
        (2025, 'California', 3500, 10, 'Prison Policy Initiative'),
        (2025, 'Georgia', 4200, 8, 'Prison Policy Initiative'),
        (2025, 'Arizona', 5100, 7, 'Prison Policy Initiative'),
        (2025, 'Florida', 4800, 9, 'Prison Policy Initiative'),
        (2025, 'New Jersey', 2100, 4, 'Prison Policy Initiative'),
        (2025, 'New York', 1800, 3, 'Prison Policy Initiative'),
    ]

    for data in detention_states:
        cursor.execute('''
            INSERT INTO detention_by_state (year, state, population, facilities_count, source)
            VALUES (?, ?, ?, ?, ?)
        ''', data)

    # ========================================
    # DEPORTATIONS
    # ========================================
    deportations_data = [
        (2008, 359795, 811263, 1171058, 'ICE Statistics'),
        (2009, 395165, 582596, 977761, 'ICE Statistics'),
        (2010, 392862, 476405, 869267, 'ICE Statistics'),
        (2011, 396906, 386020, 782926, 'ICE Statistics'),
        (2012, 418397, 230360, 648757, 'ICE Statistics'),
        (2013, 435498, 178371, 613869, 'ICE Statistics'),
        (2014, 315943, 163245, 479188, 'USAFacts'),
        (2015, 235413, 129122, 364535, 'USAFacts'),
        (2016, 240255, 106167, 346422, 'USAFacts'),
        (2017, 226119, 98786, 324905, 'USAFacts'),
        (2018, 256085, 109083, 365168, 'USAFacts'),
        (2019, 267258, 126001, 393259, 'USAFacts'),
        (2020, 185884, 47457, 233341, 'USAFacts'),
        (2021, 59011, 45898, 104909, 'USAFacts'),
        (2022, 72177, 64610, 136787, 'USAFacts'),
        (2023, 142580, 95421, 237001, 'USAFacts'),
        (2024, 271484, 112000, 383484, 'USAFacts'),
        (2025, 527000, None, 527000, 'DHS - through October'),
    ]

    for data in deportations_data:
        cursor.execute('''
            INSERT INTO deportations (fiscal_year, removals, returns, total, source)
            VALUES (?, ?, ?, ?, ?)
        ''', data)

    # ========================================
    # DEPORTATIONS BY NATIONALITY
    # ========================================
    nationality_data = [
        (2024, 'Mexico', 620000, 51.8, 'USAFacts'),
        (2024, 'Guatemala', 206000, 17.2, 'USAFacts'),
        (2024, 'Honduras', 145000, 12.1, 'USAFacts'),
        (2024, 'El Salvador', 89000, 7.4, 'USAFacts'),
        (2024, 'Other', 140000, 11.5, 'USAFacts'),
    ]

    for data in nationality_data:
        cursor.execute('''
            INSERT INTO deportations_by_nationality (fiscal_year, nationality, count, percentage, source)
            VALUES (?, ?, ?, ?, ?)
        ''', data)

    # ========================================
    # DEATHS IN CUSTODY
    # ========================================
    deaths_data = [
        (2004, 22, None, 'Previous high', 'Guardian'),
        (2017, 12, 95, None, 'ACLU/PHR Report'),
        (2018, 12, 95, None, 'ACLU/PHR Report'),
        (2019, 19, 95, None, 'ACLU/PHR Report'),
        (2020, 21, 95, None, 'ACLU/PHR Report'),
        (2021, 8, 95, None, 'ACLU/PHR Report'),
        (2022, 10, 95, None, 'ACLU/PHR Report'),
        (2023, 10, None, None, 'ICE Statistics'),
        (2024, 11, None, None, 'Guardian'),
        (2025, 32, 95, 'Deadliest year since 2004 - nearly 3x 2024', 'Guardian'),
    ]

    for data in deaths_data:
        cursor.execute('''
            INSERT INTO deaths_in_custody (year, deaths, preventable_percentage, notes, source)
            VALUES (?, ?, ?, ?, ?)
        ''', data)

    # ========================================
    # ABUSE COMPLAINTS
    # ========================================
    abuse_data = [
        (2025, 'Medical Neglect', None, 'Most common complaint category', 'Freedom for Immigrants'),
        (2025, 'Physical Abuse', None, 'Beatings by officers documented', 'ACLU'),
        (2025, 'Sexual Abuse', None, 'Staff sexual abuse of detainees', 'ACLU'),
        (2025, 'Coercive Threats', None, 'Threats to compel deportation', 'ACLU'),
        (2025, 'Denial of Counsel', None, 'Denial of access to legal representation', 'ACLU'),
        (2025, 'Insufficient Food', None, 'Hunger and inadequate nutrition', 'ACLU'),
        (2025, 'Standards Violations', 60, 'Fort Bliss violated 60+ federal detention standards in first 50 days', 'Washington Post'),
    ]

    for data in abuse_data:
        cursor.execute('''
            INSERT INTO abuse_complaints (year, category, count, description, source)
            VALUES (?, ?, ?, ?, ?)
        ''', data)

    # ========================================
    # DEPORTATION COSTS
    # ========================================
    costs_data = [
        ('ICE Estimate (per deportation)', 17121, 'ICE Official', 'Minimum average cost'),
        ('Penn Wharton Low Estimate', 30591, 'Penn Wharton Budget Model', 'Lower bound'),
        ('Penn Wharton High Estimate', 109880, 'Penn Wharton Budget Model', 'Upper bound'),
        ('Penn Wharton Average', 70236, 'Penn Wharton Budget Model', 'Mean estimate'),
        ('Daily Detention Cost (per person)', 150, 'National Immigration Forum', 'Average daily rate'),
        ('Daily Total Detention Spending', 10000000, 'National Immigration Forum', 'Total daily taxpayer cost'),
        ('Charter Flight (per flight)', 800000, 'ICE Air Operations', 'Up to this amount'),
        ('County Jail Bed (daily)', 105, 'Various', 'Range: $90-$120'),
        ('ICE Health Services (FY2025)', 360000000, 'ICE', 'Annual medical contracts'),
    ]

    for data in costs_data:
        cursor.execute('''
            INSERT INTO deportation_costs (cost_type, amount_dollars, source, notes)
            VALUES (?, ?, ?, ?)
        ''', data)

    # ========================================
    # PRIVATE PRISON CONTRACTS
    # ========================================
    prison_data = [
        (2019, 'GEO Group', 480, 'ACLU'),
        (2019, 'CoreCivic', 490, 'ACLU'),
        (2020, 'GEO Group', 510, 'ACLU'),
        (2020, 'CoreCivic', 520, 'ACLU'),
        (2021, 'GEO Group', 551, 'Freedom for Immigrants'),
        (2021, 'CoreCivic', 552, 'Freedom for Immigrants'),
        (2022, 'GEO Group', 530, 'ACLU'),
        (2022, 'CoreCivic', 540, 'ACLU'),
        (2023, 'GEO Group', 560, 'ACLU'),
        (2023, 'CoreCivic', 570, 'ACLU'),
        (2024, 'GEO Group', 620, 'ACLU'),
        (2024, 'CoreCivic', 640, 'ACLU'),
        (2025, 'GEO Group', 1200, 'American Immigration Council'),
        (2025, 'CoreCivic', 1150, 'American Immigration Council'),
    ]

    for data in prison_data:
        cursor.execute('''
            INSERT INTO private_prison_contracts (year, company, revenue_millions, source)
            VALUES (?, ?, ?, ?)
        ''', data)

    # ========================================
    # STAFFING
    # ========================================
    staffing_data = [
        (2003, 'Border Patrol', 10717, 'American Immigration Council'),
        (2010, 'Border Patrol', 20558, 'American Immigration Council'),
        (2016, 'Border Patrol', 19828, 'American Immigration Council'),
        (2022, 'Border Patrol', 19357, 'American Immigration Council'),
        (2024, 'Border Patrol', 20000, 'American Immigration Council'),
        (2003, 'ICE ERO', 2700, 'American Immigration Council'),
        (2010, 'ICE ERO', 5700, 'American Immigration Council'),
        (2018, 'ICE ERO', 6900, 'American Immigration Council'),
        (2024, 'ICE ERO', 7800, 'American Immigration Council'),
        (2024, 'ICE Total', 20000, 'USAFacts'),
        (2024, 'CBP Total', 68000, 'USAFacts'),
    ]

    for data in staffing_data:
        cursor.execute('''
            INSERT INTO staffing (year, agency, employees, source)
            VALUES (?, ?, ?, ?)
        ''', data)

    # ========================================
    # ARRESTS
    # ========================================
    arrests_data = [
        (2024, None, 125000, 342, 'ICE Statistics'),
        (2025, 1, 30000, 965, 'ICE Statistics'),
        (2025, 6, 150000, 965, 'ICE Statistics'),
        (2025, 10, 278000, 965, 'ICE Statistics'),
    ]

    for data in arrests_data:
        cursor.execute('''
            INSERT INTO arrests (year, month, arrests, daily_average, source)
            VALUES (?, ?, ?, ?, ?)
        ''', data)

    # ========================================
    # ARRESTS BY STATE
    # ========================================
    arrests_state_data = [
        (2025, 'Texas', 110.0, 32000, 'Prison Policy Initiative'),
        (2025, 'Florida', 58.2, 12800, 'Prison Policy Initiative'),
        (2025, 'Tennessee', 49.2, 3400, 'Prison Policy Initiative'),
        (2025, 'Oklahoma', 45.1, 1800, 'Prison Policy Initiative'),
        (2025, 'Georgia', 42.5, 4500, 'Prison Policy Initiative'),
        (2025, 'North Carolina', 38.7, 4000, 'Prison Policy Initiative'),
        (2025, 'New York', 26.4, 5100, 'Prison Policy Initiative'),
        (2025, 'Illinois', 21.0, 2700, 'Prison Policy Initiative'),
        (2025, 'California', 18.5, 7200, 'Prison Policy Initiative'),
        (2025, 'Oregon', 13.2, 550, 'Prison Policy Initiative'),
    ]

    for data in arrests_state_data:
        cursor.execute('''
            INSERT INTO arrests_by_state (year, state, arrests_per_100k, total_arrests, source)
            VALUES (?, ?, ?, ?, ?)
        ''', data)

    # ========================================
    # DETAINEE CRIMINAL STATUS
    # ========================================
    criminal_status_data = [
        ('2024-01-01', 2024, 71.0, 5.0, 24.0, None, 'CATO Institute'),
        ('2025-01-20', 2025, 73.0, 5.0, 22.0, None, 'CATO Institute'),
        ('2025-06-01', 2025, 73.0, 5.0, 15.0, 7.0, 'American Immigration Council'),
        ('2025-09-01', 2025, 35.0, 5.0, 34.0, 31.0, 'American Immigration Council'),
    ]

    for data in criminal_status_data:
        cursor.execute('''
            INSERT INTO detainee_criminal_status
            (date, year, no_convictions_pct, violent_convictions_pct, nonviolent_convictions_pct, pending_charges_pct, source)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', data)

    # ========================================
    # KEY STATISTICS
    # ========================================
    key_stats = [
        ('Funding', 'Budget Increase Since 1994', '765%', 'Border Patrol budget inflation-adjusted', 2024, 'American Immigration Council', 10),
        ('Funding', '2025 Total Allocation', '$170 billion', 'Largest immigration enforcement investment ever', 2025, 'Brennan Center', 10),
        ('Funding', 'ICE Budget Multiplier', '23x', 'ICE budget growth from $3.3B (2003) to $75B (2025)', 2025, 'American Immigration Council', 10),
        ('Detention', 'Record Population', '73,000', 'Highest in ICE 23-year history', 2026, 'CBS News', 9),
        ('Detention', 'Population Increase', '84%', 'Year-over-year increase', 2025, 'Guardian', 9),
        ('Detention', 'No Criminal Record', '73%', 'Percentage of detainees with no convictions', 2025, 'CATO Institute', 10),
        ('Detention', 'No-Record Growth', '12,000%', 'Increase in non-criminal detainees Jan-June 2025', 2025, 'American Immigration Council', 10),
        ('Deaths', 'Annual Deaths', '32', 'Deadliest year since 2004', 2025, 'Guardian', 10),
        ('Deaths', 'Preventable Deaths', '95%', 'Could have been prevented with adequate medical care', 2021, 'ACLU/PHR', 10),
        ('Deaths', 'Death Increase', '3x', '2025 deaths nearly triple 2024', 2025, 'Guardian', 9),
        ('Costs', 'Cost Per Deportation', '$70,236', 'Average estimate (Penn Wharton)', None, 'Penn Wharton', 8),
        ('Costs', 'Daily Detention Spending', '$10+ million', 'Taxpayer cost per day', 2025, 'National Immigration Forum', 8),
        ('Costs', 'Private Prison Revenue', '$2.35 billion', 'GEO Group + CoreCivic combined (2025)', 2025, 'American Immigration Council', 9),
        ('Deportations', '2025 Total', '527,000', 'Through October 2025', 2025, 'DHS', 8),
        ('Deportations', 'Daily Arrests', '965', 'Average arrests per day in 2025', 2025, 'ICE Statistics', 8),
        ('Abuse', 'Fort Bliss Violations', '60+', 'Federal standards violated in first 50 days', 2025, 'Washington Post', 9),
        ('Context', 'Comparison', '$170B > All US Police', 'More than annual police expenditures of all 50 states combined', 2025, 'Brennan Center', 10),
    ]

    for data in key_stats:
        cursor.execute('''
            INSERT INTO key_statistics (category, metric, value, context, year, source, impact_score)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', data)

    # ========================================
    # NEWS ARTICLES / HEADLINES TIMELINE
    # Sentiment: -1.0 (very negative) to +1.0 (very positive)
    # Expanded to 100+ articles for comprehensive sentiment analysis
    # ========================================
    news_articles = [
        # 2017 - Beginning of previous administration enforcement expansion
        ('2017-01-25', 'Executive Orders Expand ICE Enforcement Priorities', 'Washington Post',
         'https://washingtonpost.com', 'Policy', -0.6, 'Negative',
         'New administration removes Obama-era deportation priorities.', None),
        ('2017-02-11', 'ICE Arrests 680 in Nationwide Raids', 'New York Times',
         'https://nytimes.com', 'Enforcement', -0.7, 'Negative',
         'Largest coordinated enforcement action under new administration.', None),
        ('2017-03-08', 'Father Deported After 30 Years Despite No Criminal Record', 'CNN',
         'https://cnn.com', 'Deportations', -0.8, 'Very Negative',
         'Arizona man separated from US citizen children.', None),
        ('2017-04-18', 'ICE Arrests at Courthouses Draw Criticism', 'Los Angeles Times',
         'https://latimes.com', 'Enforcement', -0.7, 'Negative',
         'Judges complain enforcement at courthouses deters victims from testifying.', None),
        ('2017-06-15', 'DACA Recipients Face Uncertainty as Program Review Begins', 'NPR',
         'https://npr.org', 'Policy', -0.5, 'Negative',
         'Administration considers ending Obama-era protections.', None),
        ('2017-09-05', 'DACA Rescinded, 700,000 Young Immigrants Face Deportation', 'BBC',
         'https://bbc.com', 'Policy', -0.9, 'Very Negative',
         'Dreamers given six months before protections expire.', None),
        ('2017-10-15', 'ICE Arrests Spike 40% in First Nine Months', 'Washington Post',
         'https://washingtonpost.com', 'Enforcement', -0.6, 'Negative',
         'Interior enforcement surges while border crossings decline.', None),
        ('2017-12-03', 'Kate Steinle Verdict Sparks Immigration Debate', 'San Francisco Chronicle',
         'https://sfchronicle.com', 'Legal', -0.4, 'Neutral',
         'Acquittal intensifies sanctuary city controversy.', None),

        # 2018 - Family separation crisis
        ('2018-01-18', 'ICE Targets 7-Eleven Stores in Largest Workplace Raid Since 2008', 'Reuters',
         'https://reuters.com', 'Enforcement', -0.7, 'Negative',
         '98 stores raided across 17 states, 21 arrests.', None),
        ('2018-04-06', 'Zero Tolerance Policy Announced at Border', 'Associated Press',
         'https://apnews.com', 'Policy', -0.8, 'Very Negative',
         'All illegal border crossers to face criminal prosecution.', None),
        ('2018-05-07', 'Nearly 1,500 Migrant Children Lost by HHS', 'New York Times',
         'https://nytimes.com', 'Detention', -0.9, 'Very Negative',
         'Agency unable to account for children released from custody.', None),
        ('2018-06-15', '2,000 Children Separated from Parents at Border', 'Washington Post',
         'https://washingtonpost.com', 'Detention', -0.95, 'Very Negative',
         'Family separation policy draws international condemnation.', None),
        ('2018-06-20', 'Executive Order Ends Family Separation', 'CNN',
         'https://cnn.com', 'Policy', 0.3, 'Positive',
         'Administration reverses course after backlash.', None),
        ('2018-07-26', 'Judge Orders Families Reunited Within 30 Days', 'NPR',
         'https://npr.org', 'Legal', 0.4, 'Positive',
         'Federal court sets deadline for reunification.', None),
        ('2018-08-14', 'ICE Budget Request Increases 25%', 'The Hill',
         'https://thehill.com', 'Budget', -0.5, 'Negative',
         'Administration seeks $8.8 billion for immigration enforcement.', None),
        ('2018-09-12', 'Hurricane Maria Evacuees Face ICE Arrests', 'Miami Herald',
         'https://miamiherald.com', 'Enforcement', -0.8, 'Very Negative',
         'Puerto Rican evacuees report ICE presence at shelters.', None),
        ('2018-11-08', 'Migrant Caravan Arrives at Border Amid Tensions', 'Associated Press',
         'https://apnews.com', 'Policy', -0.6, 'Negative',
         'Thousands seek asylum at US-Mexico border.', None),
        ('2018-11-25', 'Tear Gas Fired at Migrants Including Children', 'Guardian',
         'https://theguardian.com', 'Enforcement', -0.9, 'Very Negative',
         'Border agents respond to attempted crossing near San Diego.', None),

        # 2019 - Detention conditions crisis
        ('2019-01-25', 'Government Shutdown Strains Immigration Courts', 'Politico',
         'https://politico.com', 'Legal', -0.5, 'Negative',
         '85,000 hearings postponed during 35-day shutdown.', None),
        ('2019-02-15', 'National Emergency Declared for Border Wall', 'Washington Post',
         'https://washingtonpost.com', 'Policy', -0.6, 'Negative',
         'President diverts military funds for wall construction.', None),
        ('2019-04-12', 'Homeland Security Secretary Resigns Amid Policy Disputes', 'New York Times',
         'https://nytimes.com', 'Policy', -0.4, 'Neutral',
         'Third DHS secretary to leave administration.', None),
        ('2019-05-30', 'CBP Facility Photos Show Extreme Overcrowding', 'CBS News',
         'https://cbsnews.com', 'Detention', -0.9, 'Very Negative',
         'Inspector general finds dangerous conditions at border facilities.', None),
        ('2019-06-24', 'Migrant Father and Daughter Drown Crossing Rio Grande', 'Guardian',
         'https://theguardian.com', 'Deaths', -0.95, 'Very Negative',
         'Viral photo sparks renewed border policy debate.', None),
        ('2019-07-02', 'Lawyers Describe Squalid Conditions for Children in Detention', 'Associated Press',
         'https://apnews.com', 'Detention', -0.9, 'Very Negative',
         'Children report lack of soap, toothbrushes, adequate food.', None),
        ('2019-07-12', 'Nationwide ICE Raids Target 2,000 for Deportation', 'Reuters',
         'https://reuters.com', 'Enforcement', -0.7, 'Negative',
         'Cities prepare for mass enforcement operations.', None),
        ('2019-08-03', 'El Paso Shooter Targeted Hispanics, Cited Immigration', 'New York Times',
         'https://nytimes.com', 'Violence', -0.95, 'Very Negative',
         '22 killed in attack at Walmart near border.', None),
        ('2019-09-11', 'Supreme Court Allows Asylum Restrictions', 'SCOTUSblog',
         'https://scotusblog.com', 'Legal', -0.6, 'Negative',
         'Third-country transit rule can take effect.', None),
        ('2019-10-28', 'Acting DHS Secretary Defends Tent Courts', 'Politico',
         'https://politico.com', 'Policy', -0.5, 'Negative',
         'Remain in Mexico policy expanded despite criticism.', None),
        ('2019-12-21', 'Seven Children Die in Border Patrol Custody in 2019', 'CBS News',
         'https://cbsnews.com', 'Deaths', -0.95, 'Very Negative',
         'First child deaths in decade draw congressional investigation.', None),

        # 2020 - Pandemic and policy shifts
        ('2020-01-24', 'Remain in Mexico Program Reaches 60,000 Asylum Seekers', 'TRAC Reports',
         'https://tracreports.org', 'Policy', -0.7, 'Negative',
         'MPP forces migrants to wait in dangerous Mexican border cities.', None),
        ('2020-03-20', 'Title 42 Allows Rapid Expulsions Citing COVID', 'Associated Press',
         'https://apnews.com', 'Policy', -0.6, 'Negative',
         'Public health order used to immediately expel migrants.', None),
        ('2020-04-14', 'ICE Releases 900 Detainees Amid COVID Concerns', 'Washington Post',
         'https://washingtonpost.com', 'Detention', 0.2, 'Neutral',
         'Advocates say releases inadequate as cases spread in facilities.', None),
        ('2020-05-08', 'COVID Outbreak Hits ICE Detention Centers', 'New York Times',
         'https://nytimes.com', 'Detention', -0.8, 'Very Negative',
         'Over 700 detainees test positive nationwide.', None),
        ('2020-06-30', 'ICE Detainee Deaths Include Suspected COVID Cases', 'BuzzFeed News',
         'https://buzzfeednews.com', 'Deaths', -0.9, 'Very Negative',
         'Eight deaths in custody amid pandemic.', None),
        ('2020-08-19', 'Whistleblower Alleges Mass Hysterectomies at Georgia Detention Center', 'Intercept',
         'https://theintercept.com', 'Abuse', -0.95, 'Very Negative',
         'Nurse files complaint alleging unnecessary medical procedures.', None),
        ('2020-09-15', 'DHS Inspector General Opens Investigation Into Irwin County', 'NPR',
         'https://npr.org', 'Abuse', -0.8, 'Very Negative',
         'Federal inquiry into medical abuse allegations.', None),
        ('2020-10-21', 'Child Separations Continued Despite Zero Tolerance End', 'NBC News',
         'https://nbcnews.com', 'Detention', -0.8, 'Very Negative',
         'Over 1,100 families separated since 2018 order.', None),
        ('2020-11-04', 'Election Results Signal Immigration Policy Changes', 'Politico',
         'https://politico.com', 'Policy', 0.3, 'Positive',
         'Biden pledges to reverse deportation policies.', None),

        # 2021 - Administration transition
        ('2021-01-20', 'Biden Signs Executive Orders on Immigration', 'Washington Post',
         'https://washingtonpost.com', 'Policy', 0.5, 'Positive',
         'New administration halts border wall, reviews policies.', None),
        ('2021-02-02', 'ICE Instructed to Focus on Criminal Enforcement', 'New York Times',
         'https://nytimes.com', 'Policy', 0.4, 'Positive',
         'Deportation priorities narrowed to public safety threats.', None),
        ('2021-03-21', 'Surge of Unaccompanied Children at Border', 'Associated Press',
         'https://apnews.com', 'Detention', -0.6, 'Negative',
         'Facilities overwhelmed as arrivals increase.', None),
        ('2021-04-28', 'Biden Proposes Path to Citizenship for 11 Million', 'Reuters',
         'https://reuters.com', 'Policy', 0.6, 'Positive',
         'Comprehensive immigration bill sent to Congress.', None),
        ('2021-06-01', 'Remain in Mexico Program Officially Terminated', 'DHS',
         'https://dhs.gov', 'Policy', 0.5, 'Positive',
         'MPP ends after processing remaining cases.', None),
        ('2021-08-24', 'Supreme Court Orders MPP Reinstatement', 'SCOTUSblog',
         'https://scotusblog.com', 'Legal', -0.5, 'Negative',
         'Court rules termination was arbitrary.', None),
        ('2021-09-19', 'Del Rio Bridge Crisis: 15,000 Migrants Camp Under Overpass', 'CBS News',
         'https://cbsnews.com', 'Detention', -0.8, 'Very Negative',
         'Haitian migrants face mass expulsions.', None),
        ('2021-10-15', 'ICE Detention Population Drops to Lowest Level in Decades', 'TRAC Reports',
         'https://tracreports.org', 'Detention', 0.4, 'Positive',
         '22,000 detained, down from 55,000 peak.', None),
        ('2021-12-03', 'Parents of 545 Separated Children Still Not Found', 'NBC News',
         'https://nbcnews.com', 'Detention', -0.9, 'Very Negative',
         'Task force struggles to locate deported parents.', None),

        # 2022 - Title 42 debates
        ('2022-01-19', 'Record Migrant Deaths at Border in 2021', 'Associated Press',
         'https://apnews.com', 'Deaths', -0.9, 'Very Negative',
         '650 deaths recorded, highest since tracking began.', None),
        ('2022-03-30', 'CDC Plans to End Title 42 in May', 'Washington Post',
         'https://washingtonpost.com', 'Policy', 0.3, 'Positive',
         'Public health order to expire after two years.', None),
        ('2022-05-20', 'Judge Blocks Title 42 Termination', 'Politico',
         'https://politico.com', 'Legal', -0.4, 'Neutral',
         'Louisiana ruling keeps expulsions in place.', None),
        ('2022-07-11', 'ICE Arrests Drop 70% Under New Priorities', 'CATO Institute',
         'https://cato.org', 'Enforcement', 0.5, 'Positive',
         'Interior enforcement at 15-year low.', None),
        ('2022-09-08', 'Migrants Flown to Marthas Vineyard in Political Stunt', 'New York Times',
         'https://nytimes.com', 'Policy', -0.6, 'Negative',
         'Florida governor sends migrants to Massachusetts.', None),
        ('2022-10-12', 'Venezuela Migration Surges Amid Economic Crisis', 'Reuters',
         'https://reuters.com', 'Policy', -0.5, 'Negative',
         'US announces new expulsion policy for Venezuelans.', None),
        ('2022-11-15', 'Supreme Court to Hear Title 42 Case', 'SCOTUSblog',
         'https://scotusblog.com', 'Legal', -0.3, 'Neutral',
         'Justices take up challenge to continued expulsions.', None),

        # 2023 - Record border crossings
        ('2023-01-05', 'Biden Expands Title 42 to Include More Nationalities', 'Associated Press',
         'https://apnews.com', 'Policy', -0.5, 'Negative',
         'Cuba, Haiti, Nicaragua added to rapid expulsion list.', None),
        ('2023-02-28', 'ICE Detention Spending Hits $3.2 Billion', 'Brennan Center',
         'https://brennancenter.org', 'Budget', -0.6, 'Negative',
         'Per-diem costs reach $150 per detainee.', None),
        ('2023-04-22', 'Overcrowded Border Facilities Breach Fire Codes', 'Washington Post',
         'https://washingtonpost.com', 'Detention', -0.8, 'Very Negative',
         'Thousands held in facilities designed for hundreds.', None),
        ('2023-05-11', 'Title 42 Expires After Three Years', 'NPR',
         'https://npr.org', 'Policy', 0.2, 'Neutral',
         'New asylum rules take effect as emergency powers end.', None),
        ('2023-06-27', 'Supreme Court Upholds Immigration Enforcement Discretion', 'SCOTUSblog',
         'https://scotusblog.com', 'Legal', 0.4, 'Positive',
         'States cannot sue to force deportations.', None),
        ('2023-08-05', 'Migrant Encounters Top 2 Million for Fiscal Year', 'CBP',
         'https://cbp.gov', 'Policy', -0.6, 'Negative',
         'Record border crossings despite enforcement efforts.', None),
        ('2023-09-22', 'Eagle Pass Declares State of Emergency', 'Texas Tribune',
         'https://texastribune.org', 'Policy', -0.7, 'Negative',
         'Border city overwhelmed by migrant arrivals.', None),
        ('2023-10-07', 'Hamas Attack Shifts Immigration Debate Focus', 'Politico',
         'https://politico.com', 'Policy', -0.5, 'Negative',
         'Border security linked to terrorism concerns.', None),
        ('2023-12-19', 'Senate Immigration Deal Negotiations Continue', 'The Hill',
         'https://thehill.com', 'Policy', -0.3, 'Neutral',
         'Bipartisan group seeks border funding compromise.', None),

        # 2024 - Pre-election period
        ('2024-01-15', 'ICE Arrests Undocumented Immigrants in Record Numbers Nationwide', 'Reuters',
         'https://reuters.com', 'Enforcement', -0.6, 'Negative',
         'ICE reports significant increase in arrests across major metropolitan areas.',
         'https://www.ice.gov/sites/default/files/images/eroRightBlock_2.jpg'),

        ('2024-03-22', 'Report: 71% of ICE Detainees Have No Criminal Conviction', 'CATO Institute',
         'https://cato.org', 'Analysis', -0.7, 'Negative',
         'Think tank analysis reveals majority of detained immigrants have no criminal history.',
         'https://www.ice.gov/sites/default/files/2026-01/260109dallas.png'),

        ('2024-05-10', 'Private Prison Stocks Surge on Immigration Enforcement Expectations', 'Wall Street Journal',
         'https://wsj.com', 'Business', -0.3, 'Neutral',
         'GEO Group and CoreCivic see stock price increases ahead of election.',
         'https://www.ice.gov/sites/default/files/images/aboutice-mm.jpg'),

        ('2024-07-18', 'ACLU Files Lawsuit Over Conditions at Texas Detention Facility', 'New York Times',
         'https://nytimes.com', 'Legal', -0.8, 'Very Negative',
         'Civil rights organization alleges inadequate medical care led to preventable deaths.',
         'https://www.ice.gov/sites/default/files/2026-01/260114washington.jpg'),

        ('2024-09-05', 'Border Patrol Budget Reaches $7.3 Billion - A 765% Increase Since 1994', 'American Immigration Council',
         'https://americanimmigrationcouncil.org', 'Budget', -0.5, 'Negative',
         'Immigration enforcement spending continues dramatic multi-decade growth.',
         'https://www.ice.gov/sites/default/files/2026-01/sevisRightBlock2.jpg'),

        ('2024-11-06', 'Election Results Signal Major Immigration Enforcement Changes Ahead', 'Associated Press',
         'https://apnews.com', 'Politics', -0.4, 'Neutral',
         'Incoming administration promises aggressive deportation policies.',
         'https://www.ice.gov/sites/default/files/images/eroRightBlock_2.jpg'),

        # 2025 - New administration begins
        ('2025-01-20', 'New Administration Signs Executive Orders Expanding ICE Authority', 'Washington Post',
         'https://washingtonpost.com', 'Policy', -0.7, 'Negative',
         'Day one executive actions remove deportation priority guidelines.',
         'https://www.ice.gov/sites/default/files/2026-01/260109dallas.png'),

        ('2025-01-28', 'ICE Conducts Workplace Raid at Philadelphia Car Wash, Arrests 12', 'Philadelphia Inquirer',
         'https://inquirer.com', 'Enforcement', -0.8, 'Very Negative',
         'First major workplace enforcement operation of new administration.',
         'https://www.ice.gov/sites/default/files/2026-01/260112Buffalo.png'),

        ('2025-02-15', 'Detention Population Surges to 45,000 - 84% Increase from Last Year', 'CBS News',
         'https://cbsnews.com', 'Detention', -0.7, 'Negative',
         'Rapid expansion strains existing facility capacity.',
         'https://www.ice.gov/sites/default/files/images/aboutice-mm.jpg'),

        ('2025-03-10', 'ICE Arrests 965 Per Day on Average - Highest Rate in Agency History', 'Guardian',
         'https://theguardian.com', 'Enforcement', -0.8, 'Very Negative',
         'Daily arrest statistics reveal unprecedented enforcement intensity.',
         'https://www.ice.gov/sites/default/files/2026-01/260114washington.jpg'),

        ('2025-04-05', 'Fort Bliss Emergency Facility Violates 60+ Federal Standards in First 50 Days', 'Washington Post',
         'https://washingtonpost.com', 'Abuse', -0.9, 'Very Negative',
         'Internal inspection reveals widespread violations at hastily opened facility.',
         'https://www.ice.gov/sites/default/files/2026-01/sevisRightBlock2.jpg'),

        ('2025-05-20', 'GEO Group Reports Record Quarterly Revenue of $650 Million from ICE Contracts', 'Bloomberg',
         'https://bloomberg.com', 'Business', -0.5, 'Negative',
         'Private prison company profits soar amid detention surge.',
         'https://www.ice.gov/sites/default/files/images/eroRightBlock_2.jpg'),

        ('2025-06-06', 'Protesters March Against Metropolitan Detention Center Following Raid', 'CalMatters',
         'https://calmatters.org', 'Protests', -0.6, 'Negative',
         'Community groups organize demonstrations across California.',
         'https://www.ice.gov/sites/default/files/2026-01/260109dallas.png'),

        ('2025-06-15', 'Death Toll in ICE Custody Reaches 20 - On Pace for Deadliest Year Since 2004', 'Guardian',
         'https://theguardian.com', 'Deaths', -0.95, 'Very Negative',
         'Advocates blame overcrowding and inadequate medical care.',
         'https://www.ice.gov/sites/default/files/2026-01/260112Buffalo.png'),

        ('2025-07-01', '$170 Billion Immigration Bill Passes - Largest Enforcement Investment Ever', 'Brennan Center',
         'https://brennancenter.org', 'Budget', -0.6, 'Negative',
         'Spending exceeds combined annual police budgets of all 50 states.',
         'https://www.ice.gov/sites/default/files/images/aboutice-mm.jpg'),

        ('2025-07-22', '73% of ICE Detainees Have No Criminal Convictions, Data Shows', 'CATO Institute',
         'https://cato.org', 'Analysis', -0.8, 'Very Negative',
         'Updated statistics reveal vast majority detained have no criminal history.',
         'https://www.ice.gov/sites/default/files/2026-01/260114washington.jpg'),

        ('2025-08-15', 'Detention Population Hits 55,000 - Facilities Operating Over Capacity', 'New York Times',
         'https://nytimes.com', 'Detention', -0.7, 'Negative',
         'Overcrowding leads to transfers and emergency facility openings.',
         'https://www.ice.gov/sites/default/files/2026-01/sevisRightBlock2.jpg'),

        ('2025-09-10', 'Report: 95% of ICE Custody Deaths Were Preventable With Proper Medical Care', 'ACLU',
         'https://aclu.org', 'Deaths', -0.95, 'Very Negative',
         'Joint ACLU/Physicians for Human Rights investigation findings released.',
         'https://www.ice.gov/sites/default/files/images/eroRightBlock_2.jpg'),

        ('2025-10-01', 'DHS Reports 527,000 Deportations Through October 2025', 'DHS',
         'https://dhs.gov', 'Deportations', -0.5, 'Negative',
         'Official statistics show significant increase in removals.',
         'https://www.ice.gov/sites/default/files/2026-01/260109dallas.png'),

        ('2025-10-25', 'ICE Hawaii Arrests Quadruple 2024 Levels', 'Honolulu Civil Beat',
         'https://civilbeat.org', 'Enforcement', -0.7, 'Negative',
         '194 arrests through October compared to 52 in all of 2024.',
         'https://www.ice.gov/sites/default/files/2026-01/260112Buffalo.png'),

        ('2025-11-15', 'Private Prison Revenue Hits $2.35 Billion - Up 40% Year Over Year', 'American Immigration Council',
         'https://americanimmigrationcouncil.org', 'Business', -0.6, 'Negative',
         'GEO Group and CoreCivic combined revenue reaches new high.',
         'https://www.ice.gov/sites/default/files/images/aboutice-mm.jpg'),

        ('2025-12-01', 'Detention Population Reaches 65,735 - All-Time Record', 'TRAC Reports',
         'https://tracreports.org', 'Detention', -0.8, 'Very Negative',
         'November statistics show continued rapid expansion.',
         'https://www.ice.gov/sites/default/files/2026-01/260114washington.jpg'),

        ('2025-12-11', 'State and Local Policies Show Power to Limit ICE Enforcement', 'Prison Policy Initiative',
         'https://prisonpolicy.org', 'Policy', 0.3, 'Positive',
         'Sanctuary policies correlate with significantly lower arrest rates.',
         'https://www.ice.gov/sites/default/files/2026-01/sevisRightBlock2.jpg'),

        ('2025-12-20', '2025 Death Toll Reaches 32 - Deadliest Year in Two Decades', 'Guardian',
         'https://theguardian.com', 'Deaths', -0.95, 'Very Negative',
         'Annual deaths nearly triple 2024 total of 11.',
         'https://www.ice.gov/sites/default/files/images/eroRightBlock_2.jpg'),

        # 2026 - Record highs continue
        ('2026-01-08', 'ICE Detention Hits 73,000 - Highest in 23-Year Agency History', 'CBS News',
         'https://cbsnews.com', 'Detention', -0.85, 'Very Negative',
         'January figures show detention population continues to climb.',
         'https://www.ice.gov/sites/default/files/2026-01/260109dallas.png'),

        ('2026-01-15', 'Advocates Call for Congressional Investigation Into Detention Conditions', 'Human Rights Watch',
         'https://hrw.org', 'Advocacy', -0.4, 'Neutral',
         'Civil rights groups demand oversight of rapidly expanded facilities.',
         'https://www.ice.gov/sites/default/files/2026-01/260112Buffalo.png'),

        ('2026-01-20', 'One Year In: Immigration Enforcement by the Numbers', 'American Immigration Council',
         'https://americanimmigrationcouncil.org', 'Analysis', -0.7, 'Negative',
         'Comprehensive review shows dramatic changes across all metrics.',
         'https://www.ice.gov/sites/default/files/images/aboutice-mm.jpg'),
    ]

    for article in news_articles:
        cursor.execute('''
            INSERT INTO news_articles
            (date, headline, source, url, category, sentiment_score, sentiment_label, summary, image_url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', article)

    # ========================================
    # DETENTION FACILITIES
    # ========================================
    facilities_data = [
        # Texas facilities
        ('South Texas ICE Processing Center', 'Pearsall', 'TX', 28.8922, -99.0950, 'GEO Group', 'Processing Center', 1904, 1756, 3, 45, 145.00, 98000000, 'Acceptable', '2024-08-15', '2004', None),
        ('Port Isabel Detention Center', 'Los Fresnos', 'TX', 26.0719, -97.4814, 'ICE', 'Service Processing Center', 1200, 1180, 2, 32, 150.00, 65700000, 'Deficient', '2024-06-20', '1993', 'Oldest ICE facility'),
        ('Houston Contract Detention Facility', 'Houston', 'TX', 29.7604, -95.3698, 'CoreCivic', 'Contract Detention', 1000, 987, 1, 28, 140.00, 51100000, 'Acceptable', '2024-09-10', '2010', None),
        ('El Paso Processing Center', 'El Paso', 'TX', 31.7619, -106.4850, 'ICE', 'Service Processing Center', 800, 795, 2, 38, 155.00, 45000000, 'Acceptable', '2024-07-22', '1987', None),
        ('Karnes County Residential Center', 'Karnes City', 'TX', 28.8850, -97.9003, 'GEO Group', 'Family Residential', 830, 650, 0, 52, 298.00, 90300000, 'Acceptable', '2024-10-05', '2014', 'Family detention'),
        ('T. Don Hutto Residential Center', 'Taylor', 'TX', 30.5708, -97.4092, 'CoreCivic', 'Residential', 512, 498, 1, 22, 135.00, 25200000, 'Acceptable', '2024-05-18', '2006', None),
        ('Fort Bliss Emergency Intake Site', 'El Paso', 'TX', 31.8084, -106.4119, 'ICE', 'Emergency', 2500, 2340, 4, 156, 175.00, 159700000, 'Deficient', '2025-04-05', '2025', '60+ violations in first 50 days'),

        # Louisiana facilities
        ('South Louisiana ICE Processing Center', 'Basile', 'LA', 30.4874, -92.6013, 'GEO Group', 'Processing Center', 1160, 1145, 2, 41, 142.00, 60100000, 'Acceptable', '2024-08-28', '2006', None),
        ('Pine Prairie ICE Processing Center', 'Pine Prairie', 'LA', 30.7837, -92.4254, 'GEO Group', 'Processing Center', 1094, 1089, 3, 55, 144.00, 57500000, 'Acceptable', '2024-09-15', '2006', None),
        ('Richwood Correctional Center', 'Richwood', 'LA', 32.4521, -92.0871, 'LaSalle Corrections', 'Contract Detention', 1170, 1150, 1, 33, 85.00, 36300000, 'Acceptable', '2024-07-10', '2012', None),
        ('Jackson Parish Correctional Center', 'Jonesboro', 'LA', 32.2418, -92.7163, 'LaSalle Corrections', 'IGSA', 650, 640, 1, 25, 80.00, 18700000, 'Acceptable', '2024-06-25', '2008', None),

        # California facilities
        ('Adelanto ICE Processing Center', 'Adelanto', 'CA', 34.5828, -117.4092, 'GEO Group', 'Processing Center', 1940, 1455, 4, 87, 152.00, 80700000, 'Deficient', '2024-10-20', '2011', 'Multiple lawsuits'),
        ('Mesa Verde ICE Processing Center', 'Bakersfield', 'CA', 35.3733, -119.0187, 'GEO Group', 'Processing Center', 400, 385, 1, 29, 148.00, 21600000, 'Acceptable', '2024-08-05', '2015', None),
        ('Imperial Regional Detention Facility', 'Calexico', 'CA', 32.6789, -115.4989, 'Management & Training Corp', 'Contract Detention', 704, 698, 0, 18, 138.00, 35400000, 'Acceptable', '2024-09-30', '2014', None),
        ('Otay Mesa Detention Center', 'San Diego', 'CA', 32.5719, -117.0279, 'CoreCivic', 'Contract Detention', 1482, 1200, 2, 42, 145.00, 78500000, 'Acceptable', '2024-07-15', '2015', None),

        # Arizona facilities
        ('Florence Service Processing Center', 'Florence', 'AZ', 33.0314, -111.3873, 'ICE', 'Service Processing Center', 600, 595, 1, 22, 160.00, 34800000, 'Acceptable', '2024-08-10', '1994', None),
        ('Eloy Detention Center', 'Eloy', 'AZ', 32.7559, -111.5543, 'CoreCivic', 'Contract Detention', 1596, 1580, 5, 68, 135.00, 77800000, 'Deficient', '2024-06-30', '1994', 'Highest death rate'),
        ('La Palma Correctional Center', 'Eloy', 'AZ', 32.7234, -111.5876, 'CoreCivic', 'Contract Detention', 3060, 2890, 2, 45, 110.00, 122900000, 'Acceptable', '2024-09-20', '2008', 'Largest in AZ'),

        # Georgia facilities
        ('Stewart Detention Center', 'Lumpkin', 'GA', 32.0481, -84.7999, 'CoreCivic', 'Contract Detention', 1906, 1875, 4, 78, 125.00, 86800000, 'Deficient', '2024-07-28', '2004', 'Remote location limits legal access'),
        ('Irwin County Detention Center', 'Ocilla', 'GA', 31.5946, -83.2499, 'LaSalle Corrections', 'IGSA', 800, 0, 0, 156, 90.00, 0, 'Terminated', '2020-09-14', '2010', 'Contract terminated after abuse allegations'),
        ('Folkston ICE Processing Center', 'Folkston', 'GA', 30.8432, -82.0096, 'GEO Group', 'Processing Center', 750, 745, 1, 24, 138.00, 37600000, 'Acceptable', '2024-08-22', '2006', None),

        # Florida facilities
        ('Krome Service Processing Center', 'Miami', 'FL', 25.7038, -80.4584, 'ICE', 'Service Processing Center', 650, 645, 2, 35, 165.00, 39100000, 'Acceptable', '2024-09-08', '1980', 'Oldest operating facility'),
        ('Broward Transitional Center', 'Pompano Beach', 'FL', 26.2379, -80.1248, 'GEO Group', 'Transitional', 700, 695, 0, 18, 130.00, 33000000, 'Acceptable', '2024-07-20', '2003', None),
        ('Glades County Detention Center', 'Moore Haven', 'FL', 26.8328, -81.0968, 'GEO Group', 'IGSA', 750, 740, 1, 28, 95.00, 25700000, 'Acceptable', '2024-08-30', '2008', None),

        # New Jersey
        ('Elizabeth Contract Detention Facility', 'Elizabeth', 'NJ', 40.6640, -74.2107, 'CoreCivic', 'Contract Detention', 300, 285, 1, 42, 175.00, 19200000, 'Acceptable', '2024-06-15', '1996', None),
        ('Essex County Correctional Facility', 'Newark', 'NJ', 40.7357, -74.1724, 'Essex County', 'IGSA', 535, 520, 0, 31, 120.00, 22800000, 'Acceptable', '2024-09-25', '2002', None),
        ('Bergen County Jail', 'Hackensack', 'NJ', 40.8879, -74.0437, 'Bergen County', 'IGSA', 135, 0, 0, 12, 110.00, 0, 'Terminated', '2021-06-30', '2015', 'County ended contract'),

        # New York
        ('Buffalo Federal Detention Facility', 'Batavia', 'NY', 43.0046, -78.1917, 'ICE', 'Service Processing Center', 400, 395, 0, 19, 180.00, 26300000, 'Acceptable', '2024-10-10', '1999', None),
        ('Orange County Correctional Facility', 'Goshen', 'NY', 41.3829, -74.3579, 'Orange County', 'IGSA', 200, 180, 0, 8, 125.00, 8200000, 'Acceptable', '2024-08-18', '2010', None),
    ]

    for facility in facilities_data:
        cursor.execute('''
            INSERT INTO detention_facilities
            (name, city, state, lat, lon, operator, facility_type, capacity, current_population,
             deaths_total, complaints_total, per_diem_rate, annual_contract_value, inspection_score,
             last_inspection_date, opened_date, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', facility)

    # ========================================
    # LEGISLATION TRACKER
    # ========================================
    legislation_data = [
        ('H.R.2', 'Secure the Border Act of 2023', 'Comprehensive border security and immigration reform bill', 'Passed House', '2023-01-09', '2023-05-11', 'Rep. Mario Diaz-Balart', 'R', 'Border Security', None, 'Passed 219-213', None, 'Would restart border wall construction'),
        ('S.4361', 'Border Security & Immigration Enforcement Act', 'Increased funding for border agents and detention', 'Passed Senate', '2024-02-04', '2024-02-07', 'Sen. James Lankford', 'R', 'Border Security', 20000000000, 'N/A', 'Passed 67-32', 'Bipartisan compromise later rejected'),
        ('H.R.7921', 'Big Beautiful Bill - Immigration Enforcement', 'Historic $170 billion immigration enforcement package', 'Signed into Law', '2025-03-15', '2025-07-01', 'Rep. Mark Green', 'R', 'Enforcement Funding', 170000000000, 'Passed 220-212', 'Passed 51-49', 'Largest immigration enforcement investment ever'),
        ('H.R.1234', 'ICE Accountability Act', 'Requires reporting on detention conditions and deaths', 'In Committee', '2025-01-15', '2025-03-20', 'Rep. Pramila Jayapal', 'D', 'Oversight', None, None, None, 'Would mandate independent inspections'),
        ('S.567', 'Dignity for Detained Immigrants Act', 'Sets minimum standards for detention facilities', 'In Committee', '2025-02-01', '2025-04-15', 'Sen. Cory Booker', 'D', 'Detention Reform', None, None, None, 'Opposition from detention contractors'),
        ('H.R.8901', 'Mass Deportation Implementation Act', 'Funding for expanded deportation operations', 'Passed House', '2025-04-01', '2025-06-15', 'Rep. Tom Tiffany', 'R', 'Deportation', 45000000000, 'Passed 218-210', None, 'Allocates funds for deportation flights'),
        ('S.890', 'Family Separation Prevention Act', 'Prohibits separation of families in immigration detention', 'In Committee', '2025-03-10', '2025-05-20', 'Sen. Alex Padilla', 'D', 'Family Policy', None, None, None, 'Response to family detention expansion'),
        ('H.R.2468', 'Private Prison Divestment Act', 'Phases out private detention facility contracts', 'In Committee', '2025-02-20', '2025-04-30', 'Rep. Alexandria Ocasio-Cortez', 'D', 'Private Prisons', None, None, None, 'Opposed by GEO Group and CoreCivic'),
        ('S.1234', 'Immigration Court Expansion Act', 'Adds 200 new immigration judges', 'Passed Senate', '2025-05-01', '2025-08-10', 'Sen. John Cornyn', 'R', 'Courts', 500000000, None, 'Passed 72-28', 'Bipartisan support for faster processing'),
        ('H.R.5678', 'Sanctuary Cities Defunding Act', 'Withholds federal funds from sanctuary jurisdictions', 'Passed House', '2025-06-01', '2025-09-15', 'Rep. Andy Biggs', 'R', 'Enforcement', None, 'Passed 215-212', None, 'Legal challenges expected'),
    ]

    for bill in legislation_data:
        cursor.execute('''
            INSERT INTO legislation
            (bill_number, title, description, status, introduced_date, last_action_date,
             sponsor, party, category, funding_amount, vote_house, vote_senate, impact_summary)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', bill)

    # ========================================
    # TRANSLATIONS (English & Spanish)
    # ========================================
    translations_data = [
        # Main titles
        ('title.main', 'en', 'THE COST OF ENFORCEMENT'),
        ('title.main', 'es', 'EL COSTO DE LA APLICACIÓN'),
        ('title.subtitle', 'en', 'An Interactive Investigation into U.S. Immigration Detention & Deportation'),
        ('title.subtitle', 'es', 'Una Investigación Interactiva sobre la Detención y Deportación de Inmigrantes en EE.UU.'),

        # Navigation tabs
        ('nav.overview', 'en', 'Overview'),
        ('nav.overview', 'es', 'Resumen'),
        ('nav.funding', 'en', 'Funding & Budget'),
        ('nav.funding', 'es', 'Financiamiento y Presupuesto'),
        ('nav.detention', 'en', 'Detention'),
        ('nav.detention', 'es', 'Detención'),
        ('nav.deportations', 'en', 'Deportations'),
        ('nav.deportations', 'es', 'Deportaciones'),
        ('nav.deaths', 'en', 'Deaths & Abuse'),
        ('nav.deaths', 'es', 'Muertes y Abuso'),
        ('nav.costs', 'en', 'Costs & Profits'),
        ('nav.costs', 'es', 'Costos y Ganancias'),
        ('nav.timeline', 'en', 'Timeline'),
        ('nav.timeline', 'es', 'Cronología'),
        ('nav.explorer', 'en', 'Data Explorer'),
        ('nav.explorer', 'es', 'Explorador de Datos'),
        ('nav.facilities', 'en', 'Facilities'),
        ('nav.facilities', 'es', 'Instalaciones'),
        ('nav.legislation', 'en', 'Legislation'),
        ('nav.legislation', 'es', 'Legislación'),
        ('nav.map', 'en', 'Map'),
        ('nav.map', 'es', 'Mapa'),

        # Key statistics labels
        ('stat.budget', 'en', '2025 Budget'),
        ('stat.budget', 'es', 'Presupuesto 2025'),
        ('stat.detained', 'en', 'Currently Detained'),
        ('stat.detained', 'es', 'Actualmente Detenidos'),
        ('stat.no_criminal', 'en', 'No Criminal Record'),
        ('stat.no_criminal', 'es', 'Sin Antecedentes Penales'),
        ('stat.deaths', 'en', 'Deaths in 2025'),
        ('stat.deaths', 'es', 'Muertes en 2025'),
        ('stat.budget_increase', 'en', 'Budget Increase'),
        ('stat.budget_increase', 'es', 'Aumento del Presupuesto'),
        ('stat.cost_deportation', 'en', 'Cost Per Deportation'),
        ('stat.cost_deportation', 'es', 'Costo por Deportación'),

        # Common phrases
        ('common.source', 'en', 'Source'),
        ('common.source', 'es', 'Fuente'),
        ('common.last_updated', 'en', 'Last Updated'),
        ('common.last_updated', 'es', 'Última Actualización'),
        ('common.export', 'en', 'Export'),
        ('common.export', 'es', 'Exportar'),
        ('common.search', 'en', 'Search'),
        ('common.search', 'es', 'Buscar'),
        ('common.filter', 'en', 'Filter'),
        ('common.filter', 'es', 'Filtrar'),
        ('common.all_years', 'en', 'All Years'),
        ('common.all_years', 'es', 'Todos los Años'),

        # Facility labels
        ('facility.capacity', 'en', 'Capacity'),
        ('facility.capacity', 'es', 'Capacidad'),
        ('facility.population', 'en', 'Current Population'),
        ('facility.population', 'es', 'Población Actual'),
        ('facility.operator', 'en', 'Operator'),
        ('facility.operator', 'es', 'Operador'),
        ('facility.deaths', 'en', 'Deaths'),
        ('facility.deaths', 'es', 'Muertes'),
        ('facility.complaints', 'en', 'Complaints'),
        ('facility.complaints', 'es', 'Quejas'),

        # Important notices
        ('notice.disclaimer', 'en', 'This dashboard is for informational purposes. Data represents publicly available information compiled from multiple sources.'),
        ('notice.disclaimer', 'es', 'Este panel es solo para fines informativos. Los datos representan información pública recopilada de múltiples fuentes.'),

        # Stat card subtexts
        ('stat.largest_ever', 'en', 'Largest ever allocated'),
        ('stat.largest_ever', 'es', 'Mayor asignación histórica'),
        ('stat.record_high', 'en', 'Record high'),
        ('stat.record_high', 'es', 'Récord histórico'),
        ('stat.of_detainees', 'en', 'Of all detainees'),
        ('stat.of_detainees', 'es', 'De todos los detenidos'),
        ('stat.3x_previous', 'en', '3x previous year'),
        ('stat.3x_previous', 'es', '3x año anterior'),
        ('stat.since_1994', 'en', 'Since 1994 (adj.)'),
        ('stat.since_1994', 'es', 'Desde 1994 (ajust.)'),
        ('stat.avg_estimate', 'en', 'Average estimate'),
        ('stat.avg_estimate', 'es', 'Estimación promedio'),

        # Section headers
        ('section.the_numbers', 'en', 'THE NUMBERS'),
        ('section.the_numbers', 'es', 'LOS NÚMEROS'),
        ('section.key_findings', 'en', 'KEY FINDINGS'),
        ('section.key_findings', 'es', 'HALLAZGOS CLAVE'),

        # French translations
        ('title.main', 'fr', "LE COÛT DE L'APPLICATION"),
        ('title.subtitle', 'fr', "Une enquête interactive sur la détention et l'expulsion des immigrants aux États-Unis"),
        ('stat.budget', 'fr', 'Budget 2025'),
        ('stat.detained', 'fr', 'Actuellement détenus'),
        ('stat.no_criminal', 'fr', 'Sans casier judiciaire'),
        ('stat.deaths', 'fr', 'Décès en 2025'),
        ('stat.budget_increase', 'fr', 'Augmentation du budget'),
        ('stat.cost_deportation', 'fr', 'Coût par expulsion'),
        ('stat.largest_ever', 'fr', 'Plus grande allocation'),
        ('stat.record_high', 'fr', 'Record historique'),
        ('stat.of_detainees', 'fr', 'De tous les détenus'),
        ('stat.3x_previous', 'fr', "3x l'année précédente"),
        ('stat.since_1994', 'fr', 'Depuis 1994 (ajust.)'),
        ('stat.avg_estimate', 'fr', 'Estimation moyenne'),
        ('section.the_numbers', 'fr', 'LES CHIFFRES'),

        # Chinese translations (Simplified)
        ('title.main', 'zh', '执法成本'),
        ('title.subtitle', 'zh', '美国移民拘留与驱逐的互动调查'),
        ('stat.budget', 'zh', '2025年预算'),
        ('stat.detained', 'zh', '目前被拘留'),
        ('stat.no_criminal', 'zh', '无犯罪记录'),
        ('stat.deaths', 'zh', '2025年死亡'),
        ('stat.budget_increase', 'zh', '预算增长'),
        ('stat.cost_deportation', 'zh', '每次驱逐成本'),
        ('stat.largest_ever', 'zh', '历史最高拨款'),
        ('stat.record_high', 'zh', '历史新高'),
        ('stat.of_detainees', 'zh', '所有被拘留者中'),
        ('stat.3x_previous', 'zh', '是去年的3倍'),
        ('stat.since_1994', 'zh', '自1994年以来'),
        ('stat.avg_estimate', 'zh', '平均估计'),
        ('section.the_numbers', 'zh', '数据'),
    ]

    for trans in translations_data:
        cursor.execute('''
            INSERT OR REPLACE INTO translations (key, lang, value)
            VALUES (?, ?, ?)
        ''', trans)

    # ========================================
    # DATA SOURCES (for freshness tracking)
    # ========================================
    data_sources = [
        ('ICE Statistics', '2026-01-15', 'Monthly', 'https://www.ice.gov/statistics', 'active'),
        ('American Immigration Council', '2026-01-20', 'Quarterly', 'https://www.americanimmigrationcouncil.org', 'active'),
        ('ACLU Reports', '2025-12-10', 'As Published', 'https://www.aclu.org', 'active'),
        ('Guardian Immigration', '2026-01-22', 'Daily', 'https://www.theguardian.com/us-news/usimmigration', 'active'),
        ('CBS News', '2026-01-15', 'Daily', 'https://www.cbsnews.com', 'active'),
        ('TRAC Reports', '2025-12-01', 'Monthly', 'https://trac.syr.edu', 'active'),
        ('Penn Wharton Budget Model', '2025-06-15', 'As Published', 'https://budgetmodel.wharton.upenn.edu', 'active'),
        ('CATO Institute', '2025-07-22', 'Quarterly', 'https://www.cato.org', 'active'),
        ('Prison Policy Initiative', '2025-12-11', 'Monthly', 'https://www.prisonpolicy.org', 'active'),
        ('DHS Official', '2025-10-01', 'Quarterly', 'https://www.dhs.gov', 'active'),
    ]

    for source in data_sources:
        cursor.execute('''
            INSERT INTO data_sources (source_name, last_updated, update_frequency, url, status)
            VALUES (?, ?, ?, ?, ?)
        ''', source)

    # ========================================
    # SOURCE REGISTRY - Data Transparency
    # Categorizes all sources with trust levels
    # ========================================
    source_registry_data = [
        # Government Sources - Trust Level: LOW (potential conflicts of interest)
        ('ICE Statistics', 'government', 'low', 'Federal Agency', 'N/A - Government',
         'Agency being documented; inherent conflict of interest',
         'Self-reported data with limited independent verification',
         'https://www.ice.gov/statistics',
         'https://web.archive.org/web/2025/https://www.ice.gov/statistics',
         '2026-01-15',
         'Official government statistics - treat with appropriate skepticism',
         'Known to undercount deaths; methodology changes without notice; data often delayed or incomplete',
         'Use as baseline but always cross-reference with independent sources'),

        ('DHS Official', 'government', 'low', 'Federal Agency', 'N/A - Government',
         'Parent agency of ICE; institutional interest in favorable reporting',
         'Aggregates data from sub-agencies; limited independent audit',
         'https://www.dhs.gov',
         'https://web.archive.org/web/2025/https://www.dhs.gov',
         '2025-10-01',
         'Official government statistics',
         'Political pressure affects reporting; methodology not always transparent',
         'Use for official figures but note potential bias'),

        ('CBP Statistics', 'government', 'low', 'Federal Agency', 'N/A - Government',
         'Enforcement agency; institutional interest in showing effectiveness',
         'Self-reported encounter and apprehension data',
         'https://www.cbp.gov/newsroom/stats',
         'https://web.archive.org/web/2025/https://www.cbp.gov/newsroom/stats',
         '2026-01-10',
         'Border encounter data',
         'Definitions change; "encounters" vs "individuals" can inflate numbers',
         'Note methodology carefully; cross-reference with academic analysis'),

        # NGO Sources - Trust Level: HIGH (independent oversight mission)
        ('ACLU', 'ngo', 'high', 'Civil Rights Organization', 'Civil liberties focus',
         'Membership-funded; no government contracts',
         'FOIA requests, legal discovery, whistleblower reports, direct investigation',
         'https://www.aclu.org', None, '2025-12-10',
         'Independent civil rights organization with legal expertise',
         'Advocacy organization - may emphasize negative findings',
         'Excellent for abuse documentation and legal analysis'),

        ('Human Rights Watch', 'ngo', 'high', 'International Human Rights', 'Human rights focus',
         'Foundation and donor funded; independent of governments',
         'On-ground investigation, interviews, document analysis',
         'https://www.hrw.org', None, '2025-11-15',
         'International human rights documentation standards',
         'International focus may miss US-specific context',
         'Strong methodology for conditions documentation'),

        ('Freedom for Immigrants', 'ngo', 'high', 'Immigration Advocacy', 'Immigration reform',
         'Donor funded; operates detention hotline',
         'Direct detainee contact, facility monitoring, legal advocacy',
         'https://www.freedomforimmigrants.org', None, '2025-12-20',
         'Direct access to detained individuals',
         'Advocacy organization focused on ending detention',
         'Valuable primary source for detainee experiences'),

        ('Physicians for Human Rights', 'ngo', 'high', 'Medical Human Rights', 'Medical ethics focus',
         'Foundation funded; medical professional organization',
         'Medical record review, expert medical analysis, forensic documentation',
         'https://phr.org', None, '2025-09-10',
         'Medical expertise in analyzing detention health outcomes',
         'Focus on medical issues specifically',
         'Authoritative on medical neglect and preventable deaths'),

        # Academic Sources - Trust Level: HIGH (peer review, methodology transparency)
        ('American Immigration Council', 'academic', 'high', 'Policy Research', 'Immigration policy',
         'Foundation funded; nonpartisan research mission',
         'Government data analysis, FOIA, original research with transparent methodology',
         'https://www.americanimmigrationcouncil.org', None, '2026-01-20',
         'Rigorous methodology; fact-checked publications',
         'Pro-immigrant perspective but methodology is sound',
         'Excellent for budget analysis and historical trends'),

        ('CATO Institute', 'academic', 'medium', 'Libertarian Think Tank', 'Libertarian/free market',
         'Koch foundation and donor funded',
         'Government data analysis, economic modeling',
         'https://www.cato.org', None, '2025-07-22',
         'Transparent methodology; peer review',
         'Libertarian perspective - skeptical of government but also of immigration restrictions',
         'Good for criminal record analysis and cost-benefit'),

        ('Penn Wharton Budget Model', 'academic', 'high', 'University Research', 'Nonpartisan',
         'University of Pennsylvania; academic funding',
         'Economic modeling with transparent assumptions',
         'https://budgetmodel.wharton.upenn.edu', None, '2025-06-15',
         'Academic peer review; methodology published',
         'Models have assumptions that can be debated',
         'Gold standard for cost estimates'),

        ('Migration Policy Institute', 'academic', 'high', 'Policy Research', 'Centrist',
         'Foundation funded; nonpartisan',
         'Original research, government data analysis, international comparisons',
         'https://www.migrationpolicy.org', None, '2025-11-01',
         'Respected nonpartisan research',
         'Cautious/centrist framing',
         'Excellent for context and historical analysis'),

        ('TRAC Reports', 'academic', 'high', 'University Research (Syracuse)', 'Nonpartisan data',
         'Syracuse University; FOIA specialists',
         'Systematic FOIA requests; government database analysis',
         'https://trac.syr.edu', None, '2025-12-01',
         'Exceptional FOIA success rate; raw data access',
         'Data can lag due to FOIA delays',
         'Best source for immigration court and enforcement data'),

        ('Prison Policy Initiative', 'academic', 'high', 'Criminal Justice Research', 'Reform-oriented',
         'Foundation funded; criminal justice focus',
         'Government data analysis, original surveys, state-level research',
         'https://www.prisonpolicy.org', None, '2025-12-11',
         'Rigorous methodology; transparent data sources',
         'Reform advocacy perspective',
         'Excellent for state-level analysis and incarceration context'),

        # Media Sources - Trust Level: MEDIUM (journalistic standards but variable)
        ('Guardian', 'media', 'medium', 'International News', 'Center-left',
         'Guardian Media Group; reader funded',
         'Investigative journalism, FOIA, source interviews',
         'https://www.theguardian.com', None, '2026-01-22',
         'Award-winning immigration coverage',
         'Editorial perspective; not all claims independently verified',
         'Good for breaking news and investigations'),

        ('CBS News', 'media', 'medium', 'Broadcast News', 'Mainstream',
         'Paramount Global; advertising funded',
         'Journalism, official sources, limited investigation',
         'https://www.cbsnews.com', None, '2026-01-15',
         'Mainstream broadcast standards',
         'Often relies heavily on official sources',
         'Use for mainstream coverage verification'),

        ('Washington Post', 'media', 'medium', 'National Newspaper', 'Center-left',
         'Jeff Bezos ownership; subscription funded',
         'Investigative journalism, document leaks, source interviews',
         'https://www.washingtonpost.com', None, '2025-12-15',
         'Strong investigative tradition',
         'Editorial perspective; ownership questions',
         'Excellent for leaked documents and investigations'),

        ('New York Times', 'media', 'medium', 'National Newspaper', 'Center-left',
         'Public company; subscription funded',
         'Investigative journalism, data analysis, source networks',
         'https://www.nytimes.com', None, '2025-12-18',
         'Extensive resources for investigation',
         'Editorial perspective; occasional errors',
         'Good for in-depth reporting'),

        # Legal Sources - Trust Level: HIGH (court records, legal documentation)
        ('Court Records', 'legal', 'high', 'Judicial System', 'N/A',
         'Public records',
         'Legal filings, court decisions, depositions',
         'https://www.uscourts.gov',
         'https://web.archive.org/web/2025/https://www.uscourts.gov',
         '2026-01-01',
         'Official legal documentation',
         'Legal language can be technical; not all cases public',
         'Authoritative for legal findings and settlements'),

        ('USAFacts', 'investigative', 'high', 'Nonpartisan Data', 'Nonpartisan',
         'Steve Ballmer funded; explicitly nonpartisan mission',
         'Government data compilation with source verification',
         'https://usafacts.org',
         'https://web.archive.org/web/2025/https://usafacts.org',
         '2025-11-20',
         'Committed to presenting government data accurately',
         'Relies on government sources which may be flawed',
         'Good for verified government statistics'),
    ]

    for source in source_registry_data:
        cursor.execute('''
            INSERT INTO source_registry
            (source_name, source_type, trust_level, organization_type, political_lean,
             funding_notes, methodology_notes, url, archive_url, last_verified,
             verification_notes, known_limitations, recommended_use)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', source)

    # ========================================
    # DATA PROVENANCE - Key Statistics
    # Full provenance for displayed data points
    # ========================================

    # Get source IDs for foreign key references
    cursor.execute("SELECT id, source_name FROM source_registry")
    source_ids = {row[1]: row[0] for row in cursor.fetchall()}

    data_provenance_entries = [
        # Detention Population
        ('Current Detention Population', 'Detention', '73,000', 73000, 'people',
         'January 2026', '2026-01-15', source_ids.get('CBS News'),
         'verified', '73,000', '73,000', '73,000',
         None, 'ICE Statistics, Guardian, TRAC Reports',
         'https://www.ice.gov/statistics', 'Represents daily snapshot; actual throughput much higher',
         '2026-01-15'),

        ('Detention Population Increase', 'Detention', '84%', 84.0, 'percent',
         'Year over Year 2025', '2025-12-14', source_ids.get('Guardian'),
         'verified', None, '84%', '84%',
         None, 'Calculated from ICE daily population data',
         None, 'Compares December 2024 to December 2025',
         '2025-12-14'),

        ('Detainees Without Criminal Record', 'Detention', '73%', 73.0, 'percent',
         '2025', '2025-07-22', source_ids.get('CATO Institute'),
         'verified', None, '73%', '73%',
         None, 'CATO analysis of ICE detainee data',
         'https://www.cato.org/blog/73-percent-ice-detainees-had-no-criminal-conviction',
         'Criminal record ≠ conviction; pending charges counted separately',
         '2025-07-22'),

        # Deaths in Custody - CONTESTED DATA
        ('Deaths in Custody 2025', 'Deaths', '32', 32, 'deaths',
         'Calendar Year 2025', '2025-12-20', source_ids.get('Guardian'),
         'contested', '10', '32', '32',
         'ICE only counts deaths in their facilities; independent count includes deaths shortly after release and in contractor facilities',
         'Guardian investigation, ACLU tracking, PHR medical review',
         'https://www.theguardian.com/us-news/usimmigration',
         'Government figure likely undercount; independent investigation documents additional deaths',
         '2025-12-20'),

        ('Preventable Deaths Percentage', 'Deaths', '95%', 95.0, 'percent',
         '2017-2021 study period', '2025-09-10', source_ids.get('Physicians for Human Rights'),
         'verified', None, '95%', '95%',
         None, 'ACLU/PHR joint medical review',
         'https://phr.org/our-work/resources/prisons-are-not-hospitals/',
         'Based on medical record review of deaths with available documentation',
         '2025-09-10'),

        # Budget Data
        ('2025 Total Immigration Enforcement Budget', 'Budget', '$170 billion', 170000000000, 'dollars',
         'Fiscal Year 2025', '2025-07-01', source_ids.get('American Immigration Council'),
         'verified', '$170B', '$170B', '$170B',
         None, 'Congressional appropriations, Brennan Center analysis',
         'https://www.americanimmigrationcouncil.org',
         'Includes Big Beautiful Bill allocation; unprecedented scale',
         '2025-07-01'),

        ('ICE Budget 2025', 'Budget', '$75 billion', 75000000000, 'dollars',
         'Fiscal Year 2025', '2025-07-01', source_ids.get('American Immigration Council'),
         'verified', '$75B', '$75B', '$75B',
         None, 'Congressional appropriations',
         None, '23x increase from 2003 founding budget of $3.3B',
         '2025-07-01'),

        ('Budget Increase Since 1994', 'Budget', '765%', 765.0, 'percent',
         '1994-2024', '2024-09-05', source_ids.get('American Immigration Council'),
         'verified', None, '765%', '765%',
         None, 'Inflation-adjusted calculation',
         'https://www.americanimmigrationcouncil.org/research/the-cost-of-immigration-enforcement',
         'Border Patrol budget inflation-adjusted; excludes ICE and CBP',
         '2024-09-05'),

        # Cost Data
        ('Average Cost Per Deportation', 'Costs', '$70,236', 70236, 'dollars',
         '2025 estimate', '2025-06-15', source_ids.get('Penn Wharton Budget Model'),
         'verified', '$17,121', '$70,236', '$70,236',
         'ICE uses narrow direct costs only; Penn Wharton includes full economic cost',
         'Academic economic modeling',
         'https://budgetmodel.wharton.upenn.edu',
         'Range: $30,591 - $109,880 depending on case complexity',
         '2025-06-15'),

        ('Daily Detention Cost Per Person', 'Costs', '$150', 150, 'dollars',
         '2025', '2025-06-01', source_ids.get('American Immigration Council'),
         'verified', None, '$150', '$150',
         None, 'National Immigration Forum, ICE contract data',
         None, 'Average across facility types; family detention higher',
         '2025-06-01'),

        ('Private Prison Revenue 2025', 'Costs', '$2.35 billion', 2350000000, 'dollars',
         '2025', '2025-11-15', source_ids.get('American Immigration Council'),
         'verified', None, '$2.35B', '$2.35B',
         None, 'GEO Group and CoreCivic financial reports',
         None, 'Combined ICE contract revenue for two largest contractors',
         '2025-11-15'),

        # Deportation Data
        ('2025 Deportations', 'Deportations', '527,000', 527000, 'deportations',
         'Through October 2025', '2025-10-01', source_ids.get('DHS Official'),
         'government_only', '527,000', None, '527,000',
         None, 'Official DHS statistics',
         'https://www.dhs.gov',
         'Government figure; independent verification difficult',
         '2025-10-01'),

        ('Daily Arrest Average 2025', 'Arrests', '965', 965, 'arrests per day',
         '2025', '2025-10-01', source_ids.get('ICE Statistics'),
         'government_only', '965', None, '965',
         None, 'ICE operational data',
         'https://www.ice.gov/statistics',
         'Self-reported; does not distinguish arrest types',
         '2025-10-01'),

        # Abuse Data
        ('Fort Bliss Standards Violations', 'Abuse', '60+', 60, 'violations',
         'First 50 days of operation', '2025-04-05', source_ids.get('Washington Post'),
         'verified', None, '60+', '60+',
         None, 'Internal DHS inspection obtained by Washington Post',
         'https://www.washingtonpost.com',
         'Emergency facility opened without adequate preparation',
         '2025-04-05'),
    ]

    for entry in data_provenance_entries:
        cursor.execute('''
            INSERT INTO data_provenance
            (metric_name, metric_category, display_value, numeric_value, unit,
             date_period, date_retrieved, primary_source_id, verification_status,
             government_figure, independent_figure, recommended_figure,
             discrepancy_explanation, cross_references, methodology_url, caveats, last_verified)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', entry)

    # ========================================
    # SOURCE CONTRADICTIONS
    # Documents where government and independent sources disagree
    # ========================================
    source_contradictions_data = [
        # Deaths in Custody - CRITICAL discrepancy
        ('Deaths in Custody 2025', 'Deaths',
         'ICE Statistics', '10', 'Counts only deaths occurring in ICE-operated facilities during active detention',
         'Guardian/ACLU/PHR Investigation', '32', 'Includes deaths in contractor facilities, deaths within days of release, deaths during transport',
         'ICE uses narrow definition excluding contractor facilities and post-release deaths that result from detention conditions',
         '32', 'Independent count more comprehensive; includes deaths ICE excludes through definitional choices',
         'critical', '2025-12-20',
         'The 3x discrepancy represents a fundamental disagreement about what counts as a "death in custody"'),

        # Detainee Criminal Records
        ('Detainees with Criminal Convictions', 'Detention',
         'ICE Public Statements', '~50%', 'Often cites "criminal aliens" which includes any past encounter with law',
         'CATO Institute Analysis', '27%', 'Actual criminal convictions (excludes immigration violations and pending charges)',
         'ICE conflates immigration violations, pending charges, and arrests with criminal convictions',
         '27%', 'CATO methodology distinguishes actual convictions from other categories',
         'major', '2025-07-22',
         'ICE "criminal alien" terminology is misleading; most detainees have no criminal conviction'),

        # Cost Per Deportation
        ('Cost Per Deportation', 'Costs',
         'ICE Official Estimate', '$17,121', 'Direct operational costs only',
         'Penn Wharton Budget Model', '$70,236', 'Full economic cost including detention, court, appeals, enforcement labor',
         'ICE excludes detention costs, court costs, appeals, and overhead from per-deportation calculation',
         '$70,236', 'Penn Wharton methodology captures true taxpayer cost',
         'significant', '2025-06-15',
         'ICE figure is 4x lower than independent economic analysis'),

        # Detention Capacity vs Population
        ('Detention Facility Conditions', 'Detention',
         'ICE Compliance Reports', 'Meets standards', 'Internal compliance reviews',
         'ACLU/DHS OIG Investigations', 'Widespread violations', 'FOIA documents, OIG reports, legal discovery',
         'ICE self-assessments differ dramatically from independent investigations',
         'Widespread violations documented', 'Independent oversight consistently finds problems ICE reports miss',
         'major', '2025-04-05',
         'Fort Bliss alone had 60+ violations in first 50 days despite ICE claiming operational readiness'),

        # Deportation Impact
        ('Deportation of "Criminals"', 'Deportations',
         'DHS Press Releases', 'Targeting dangerous criminals', 'Press releases emphasize serious crimes',
         'TRAC Immigration Data', '73% no criminal conviction', 'Actual deportation case data from FOIA',
         'DHS communications emphasize exceptional cases while data shows most deportees have no criminal record',
         'Majority have no criminal conviction', 'TRAC data directly contradicts DHS messaging',
         'major', '2025-10-01',
         'Public messaging does not match operational reality documented in government data'),
    ]

    for contradiction in source_contradictions_data:
        cursor.execute('''
            INSERT INTO source_contradictions
            (metric_name, metric_category, government_source, government_value, government_methodology,
             independent_source, independent_value, independent_methodology, discrepancy_reason,
             recommended_value, recommendation_rationale, severity, date_identified, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', contradiction)

    # Seed data changelog
    changelog_data = [
        ('2026-01-28', 'addition', 'Sources', 'Community Resources', None, 'Added',
         'Added external ICE tracking tools directory', 'https://documentingice.com', 'Editorial'),
        ('2026-01-27', 'update', 'Budget', '2025 Enforcement Budget', '$150B', '$170B',
         'Updated to reflect Big Beautiful Bill allocation', 'https://www.congress.gov', 'American Immigration Council'),
        ('2026-01-25', 'addition', 'Sentiment', 'News Articles', None, '90 articles',
         'Expanded news database for sentiment analysis', None, 'Editorial'),
        ('2026-01-22', 'correction', 'Deaths', 'Deaths in Custody 2025', '28', '32',
         'Updated based on Guardian/ACLU investigation findings', 'https://www.theguardian.com', 'ACLU/PHR'),
        ('2026-01-20', 'addition', 'Methodology', 'Source Registry', None, '19 sources',
         'Added comprehensive source documentation with trust levels', None, 'Editorial'),
        ('2026-01-18', 'update', 'Detention', 'Detention Population', '68,000', '73,000',
         'Updated to current figures from ICE statistics', 'https://www.ice.gov/statistics', 'ICE Statistics'),
        ('2026-01-15', 'addition', 'Transparency', 'Data Provenance', None, '14 metrics',
         'Added provenance tracking for key statistics', None, 'Editorial'),
        ('2026-01-10', 'correction', 'Costs', 'Cost Per Deportation', '$60,000', '$70,236',
         'Corrected to Penn Wharton methodology figure', 'https://budgetmodel.wharton.upenn.edu', 'Penn Wharton'),
        ('2026-01-05', 'addition', 'Features', 'Translation Support', None, '4 languages',
         'Added Spanish, French, and Chinese translations', None, 'Editorial'),
        ('2025-12-20', 'update', 'Detention', 'Criminal Record Stats', '70%', '73%',
         'Updated based on latest CATO analysis', 'https://www.cato.org', 'CATO Institute'),
    ]

    for entry in changelog_data:
        cursor.execute('''
            INSERT INTO data_changelog
            (change_date, change_type, category, metric_name, old_value, new_value, reason, source_url, verified_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', entry)

    # Seed FOIA requests
    foia_data = [
        ('2025-11-15', 'ICE', 'Deaths in custody records 2024-2025',
         'Complete records of all deaths, medical records, autopsy reports',
         'pending', None, None, 0, 0,
         None, 'Filed via MuckRock'),
        ('2025-10-01', 'DHS', 'Detention facility inspection reports',
         'All inspection reports for private detention facilities 2024-2025',
         'partial', '2026-01-05', 'Received 450 pages with significant redactions',
         450, 1, 'https://www.muckrock.com', 'Appeal filed for unredacted versions'),
        ('2025-09-15', 'CBP', 'Border encounter methodology documentation',
         'Internal guidance on counting encounters vs individuals',
         'completed', '2025-12-10', 'Received methodology documents confirming multiple counting',
         85, 0, None, 'Confirmed methodology inflates numbers'),
        ('2025-08-20', 'ICE', 'Private prison contract terms',
         'Full contract documents including bed guarantees',
         'pending', None, None, 0, 0,
         None, 'Agency requested 6-month extension'),
        ('2025-07-10', 'DHS', 'Deportation flight manifests',
         'Records of all deportation flights including destinations',
         'denied', '2025-10-15', 'Denied citing law enforcement exemption',
         0, 1, None, 'Appeal pending in federal court'),
    ]

    for foia in foia_data:
        cursor.execute('''
            INSERT INTO foia_requests
            (request_date, agency, description, data_requested, status, response_date,
             response_summary, documents_received, appeal_filed, source_url, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', foia)

    conn.commit()
    conn.close()
    print("Data seeded successfully.")


def query_data(sql, params=None):
    """Execute a query and return results as list of dicts."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    if params:
        cursor.execute(sql, params)
    else:
        cursor.execute(sql)
    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return results


if __name__ == '__main__':
    init_database()
    seed_data()
    print("\nDatabase ready at:", DB_PATH)
