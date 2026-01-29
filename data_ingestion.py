"""
Data Ingestion Module for Project Watchtower
Handles fetching data from external APIs and storing in database.

Supported sources:
- USASpending.gov (Federal contracts)
- OpenSecrets (Lobbying data) - placeholder
- SEC EDGAR (Corporate filings) - placeholder
"""

import requests
import json
from datetime import datetime, timedelta
from time import sleep
from database import get_connection, adapt_query, USE_POSTGRES

# API Configuration
USASPENDING_BASE_URL = "https://api.usaspending.gov/api/v2"
USASPENDING_RATE_LIMIT = 0.5  # seconds between requests

# DHS/ICE related agency codes
DHS_AGENCY_CODES = {
    "070": "Department of Homeland Security",
    "7003": "U.S. Immigration and Customs Enforcement",
    "7012": "U.S. Customs and Border Protection",
    "7022": "U.S. Citizenship and Immigration Services",
}

# Keywords for immigration enforcement contracts
ICE_KEYWORDS = [
    "detention", "immigration", "deportation", "removal",
    "enforcement", "border", "custody", "alien",
    "correctional", "prison", "incarceration"
]

# Major detention contractors to track
MAJOR_CONTRACTORS = [
    "GEO GROUP",
    "CORECIVIC",
    "MANAGEMENT AND TRAINING CORPORATION",
    "CALIBURN",
    "PALANTIR",
    "LEXISNEXIS",
    "CLEARVIEW",
]


class USASpendingClient:
    """Client for USASpending.gov API v2."""

    def __init__(self):
        self.base_url = USASPENDING_BASE_URL
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json"
        })

    def _make_request(self, endpoint, method="POST", data=None, params=None):
        """Make a rate-limited request to the API."""
        url = f"{self.base_url}/{endpoint}"

        try:
            if method == "POST":
                response = self.session.post(url, json=data, params=params, timeout=30)
            else:
                response = self.session.get(url, params=params, timeout=30)

            response.raise_for_status()
            sleep(USASPENDING_RATE_LIMIT)  # Rate limiting
            return response.json()

        except requests.exceptions.RequestException as e:
            print(f"API request failed: {e}")
            return None

    def search_contracts(self, filters, page=1, limit=100):
        """
        Search for contracts using the advanced search endpoint.

        Args:
            filters: Dictionary of search filters
            page: Page number (1-indexed)
            limit: Results per page (max 100)

        Returns:
            Dictionary with results and pagination info
        """
        endpoint = "search/spending_by_award"

        payload = {
            "filters": filters,
            "fields": [
                "Award ID", "Recipient Name", "Award Amount",
                "Total Outlays", "Description", "Contract Award Type",
                "Start Date", "End Date", "Awarding Agency", "Awarding Sub Agency",
                "recipient_id", "Place of Performance City", "Place of Performance State Code",
                "NAICS Code", "NAICS Description", "Extent Competed",
                "Type of Contract Pricing", "generated_internal_id"
            ],
            "page": page,
            "limit": limit,
            "sort": "Award Amount",
            "order": "desc",
            "subawards": False
        }

        return self._make_request(endpoint, data=payload)

    def get_award_details(self, award_id):
        """Get detailed information about a specific award."""
        endpoint = f"awards/{award_id}/"
        return self._make_request(endpoint, method="GET")

    def get_recipient_profile(self, recipient_id):
        """Get recipient (contractor) profile."""
        endpoint = f"recipient/{recipient_id}/"
        return self._make_request(endpoint, method="GET")

    def search_dhs_contracts(self, fiscal_year=None, keyword=None, min_amount=10000):
        """
        Search for DHS/ICE contracts.

        Args:
            fiscal_year: Fiscal year to search (default: current)
            keyword: Additional keyword filter
            min_amount: Minimum contract value

        Returns:
            List of contract records
        """
        if fiscal_year is None:
            fiscal_year = datetime.now().year

        filters = {
            "agencies": [
                {"type": "awarding", "tier": "toptier", "name": "Department of Homeland Security"}
            ],
            "time_period": [
                {"start_date": f"{fiscal_year - 1}-10-01", "end_date": f"{fiscal_year}-09-30"}
            ],
            "award_type_codes": ["A", "B", "C", "D"],  # Contract types
            "award_amounts": [{"lower_bound": min_amount}]
        }

        if keyword:
            filters["keywords"] = [keyword]

        all_results = []
        page = 1

        while True:
            response = self.search_contracts(filters, page=page)
            if not response or "results" not in response:
                break

            results = response.get("results", [])
            if not results:
                break

            all_results.extend(results)
            print(f"  Fetched page {page}: {len(results)} contracts")

            # Check if more pages exist
            if len(results) < 100:
                break
            page += 1

            # Safety limit
            if page > 50:
                print("  Reached page limit, stopping")
                break

        return all_results

    def search_contractor_contracts(self, contractor_name, fiscal_years=None):
        """Search for all contracts awarded to a specific contractor."""
        if fiscal_years is None:
            current_year = datetime.now().year
            fiscal_years = list(range(current_year - 5, current_year + 1))

        all_contracts = []

        for fy in fiscal_years:
            filters = {
                "recipient_search_text": [contractor_name],
                "time_period": [
                    {"start_date": f"{fy - 1}-10-01", "end_date": f"{fy}-09-30"}
                ],
                "award_type_codes": ["A", "B", "C", "D"],
            }

            response = self.search_contracts(filters)
            if response and "results" in response:
                all_contracts.extend(response["results"])

        return all_contracts


def ingest_dhs_contracts(fiscal_year=None, keywords=None):
    """
    Ingest DHS/ICE contracts from USASpending.gov.

    Args:
        fiscal_year: Fiscal year to ingest (default: current and previous)
        keywords: List of keywords to search (default: ICE_KEYWORDS)
    """
    client = USASpendingClient()
    conn = get_connection()
    cursor = conn.cursor()

    if fiscal_year is None:
        current_year = datetime.now().year
        fiscal_years = [current_year, current_year - 1]
    else:
        fiscal_years = [fiscal_year]

    if keywords is None:
        keywords = ICE_KEYWORDS + [None]  # None = no keyword filter

    total_inserted = 0

    for fy in fiscal_years:
        print(f"\nIngesting FY{fy} contracts...")

        for keyword in keywords:
            kw_display = keyword or "ALL DHS"
            print(f"  Searching: {kw_display}")

            contracts = client.search_dhs_contracts(fiscal_year=fy, keyword=keyword)
            print(f"  Found {len(contracts)} contracts")

            for contract in contracts:
                try:
                    # Check for sole source / no-bid
                    extent_competed = contract.get("Extent Competed", "")
                    is_sole_source = "sole source" in str(extent_competed).lower()
                    is_no_bid = extent_competed in ["NOT COMPETED", "NOT AVAILABLE FOR COMPETITION"]

                    # Prepare insert
                    insert_sql = adapt_query('''
                        INSERT INTO federal_contracts (
                            award_id, award_description, naics_code, naics_description,
                            awarding_agency, awarding_sub_agency, recipient_name,
                            total_obligation, period_of_performance_start,
                            period_of_performance_end, extent_competed,
                            type_of_contract_pricing, place_of_performance_city,
                            place_of_performance_state, is_sole_source, is_no_bid,
                            raw_data, date_ingested
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ON CONFLICT(award_id) DO UPDATE SET
                            total_obligation = excluded.total_obligation,
                            period_of_performance_end = excluded.period_of_performance_end,
                            raw_data = excluded.raw_data,
                            date_ingested = excluded.date_ingested
                    ''') if USE_POSTGRES else '''
                        INSERT OR REPLACE INTO federal_contracts (
                            award_id, award_description, naics_code, naics_description,
                            awarding_agency, awarding_sub_agency, recipient_name,
                            total_obligation, period_of_performance_start,
                            period_of_performance_end, extent_competed,
                            type_of_contract_pricing, place_of_performance_city,
                            place_of_performance_state, is_sole_source, is_no_bid,
                            raw_data, date_ingested
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    '''

                    params = (
                        contract.get("Award ID"),
                        contract.get("Description"),
                        contract.get("NAICS Code"),
                        contract.get("NAICS Description"),
                        contract.get("Awarding Agency"),
                        contract.get("Awarding Sub Agency"),
                        contract.get("Recipient Name"),
                        contract.get("Award Amount"),
                        contract.get("Start Date"),
                        contract.get("End Date"),
                        extent_competed,
                        contract.get("Type of Contract Pricing"),
                        contract.get("Place of Performance City"),
                        contract.get("Place of Performance State Code"),
                        1 if is_sole_source else 0,
                        1 if is_no_bid else 0,
                        json.dumps(contract),
                        datetime.now().strftime("%Y-%m-%d")
                    )

                    cursor.execute(adapt_query(insert_sql), params)
                    total_inserted += 1

                except Exception as e:
                    print(f"    Error inserting contract: {e}")
                    continue

            conn.commit()

    conn.close()
    print(f"\nIngestion complete. Total contracts: {total_inserted}")
    return total_inserted


def ingest_major_contractors():
    """Ingest contract data for major detention/surveillance contractors."""
    client = USASpendingClient()
    conn = get_connection()
    cursor = conn.cursor()

    print("Ingesting major contractor data...")

    for contractor in MAJOR_CONTRACTORS:
        print(f"\n  Processing: {contractor}")
        contracts = client.search_contractor_contracts(contractor)
        print(f"    Found {len(contracts)} contracts")

        # Calculate totals
        total_value = sum(c.get("Award Amount", 0) or 0 for c in contracts)
        ice_value = sum(
            c.get("Award Amount", 0) or 0
            for c in contracts
            if "IMMIGRATION" in str(c.get("Awarding Sub Agency", "")).upper()
        )
        dhs_value = sum(
            c.get("Award Amount", 0) or 0
            for c in contracts
            if "HOMELAND" in str(c.get("Awarding Agency", "")).upper()
        )

        # Upsert contractor record
        insert_sql = '''
            INSERT INTO corporate_contractors (
                name, total_ice_contracts, total_dhs_contracts,
                total_federal_contracts, last_updated
            ) VALUES (?, ?, ?, ?, ?)
        '''

        try:
            cursor.execute(adapt_query(insert_sql), (
                contractor,
                ice_value,
                dhs_value,
                total_value,
                datetime.now().strftime("%Y-%m-%d")
            ))
        except Exception as e:
            # Update if exists
            update_sql = '''
                UPDATE corporate_contractors SET
                    total_ice_contracts = ?,
                    total_dhs_contracts = ?,
                    total_federal_contracts = ?,
                    last_updated = ?
                WHERE name = ?
            '''
            cursor.execute(adapt_query(update_sql), (
                ice_value, dhs_value, total_value,
                datetime.now().strftime("%Y-%m-%d"),
                contractor
            ))

        conn.commit()

    conn.close()
    print("\nContractor ingestion complete.")


def analyze_sole_source_contracts():
    """Analyze prevalence of sole-source/no-bid contracts."""
    conn = get_connection()
    cursor = conn.cursor()

    # Overall stats
    cursor.execute(adapt_query('''
        SELECT
            COUNT(*) as total_contracts,
            SUM(CASE WHEN is_sole_source = 1 THEN 1 ELSE 0 END) as sole_source_count,
            SUM(CASE WHEN is_no_bid = 1 THEN 1 ELSE 0 END) as no_bid_count,
            SUM(total_obligation) as total_value,
            SUM(CASE WHEN is_sole_source = 1 THEN total_obligation ELSE 0 END) as sole_source_value,
            SUM(CASE WHEN is_no_bid = 1 THEN total_obligation ELSE 0 END) as no_bid_value
        FROM federal_contracts
        WHERE awarding_agency LIKE '%Homeland%'
    '''))

    row = cursor.fetchone()

    if row:
        total, sole_count, no_bid_count, total_val, sole_val, no_bid_val = row
        print("\n=== Sole Source / No-Bid Analysis ===")
        print(f"Total DHS Contracts: {total:,}")
        print(f"Sole Source: {sole_count:,} ({100*sole_count/total:.1f}%)")
        print(f"No-Bid: {no_bid_count:,} ({100*no_bid_count/total:.1f}%)")
        print(f"\nTotal Contract Value: ${total_val:,.0f}")
        print(f"Sole Source Value: ${sole_val:,.0f} ({100*sole_val/total_val:.1f}%)")
        print(f"No-Bid Value: ${no_bid_val:,.0f} ({100*no_bid_val/total_val:.1f}%)")

    # By contractor
    cursor.execute(adapt_query('''
        SELECT
            recipient_name,
            COUNT(*) as contract_count,
            SUM(total_obligation) as total_value,
            SUM(CASE WHEN is_sole_source = 1 OR is_no_bid = 1 THEN 1 ELSE 0 END) as non_competitive_count,
            SUM(CASE WHEN is_sole_source = 1 OR is_no_bid = 1 THEN total_obligation ELSE 0 END) as non_competitive_value
        FROM federal_contracts
        WHERE awarding_agency LIKE '%Homeland%'
        GROUP BY recipient_name
        ORDER BY total_value DESC
        LIMIT 20
    '''))

    print("\n=== Top Recipients by Non-Competitive Awards ===")
    for row in cursor.fetchall():
        name, count, total, nc_count, nc_val = row
        if total and nc_val:
            pct = 100 * nc_val / total
            print(f"{name[:40]:<40} ${total:>15,.0f}  Non-comp: {pct:.0f}%")

    conn.close()


def get_contract_summary_for_visualization():
    """Get contract data formatted for Sankey/flow visualization."""
    conn = get_connection()
    cursor = conn.cursor()

    # Get flows by agency -> contractor
    cursor.execute(adapt_query('''
        SELECT
            awarding_sub_agency,
            recipient_name,
            SUM(total_obligation) as value
        FROM federal_contracts
        WHERE awarding_agency LIKE '%Homeland%'
            AND total_obligation > 1000000
        GROUP BY awarding_sub_agency, recipient_name
        ORDER BY value DESC
        LIMIT 50
    '''))

    flows = []
    for row in cursor.fetchall():
        agency, recipient, value = row
        flows.append({
            "source": agency or "DHS (Other)",
            "target": recipient,
            "value": value
        })

    conn.close()
    return flows


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "ingest":
            print("Starting DHS contract ingestion...")
            ingest_dhs_contracts()
            ingest_major_contractors()

        elif command == "analyze":
            analyze_sole_source_contracts()

        elif command == "test":
            print("Testing USASpending API connection...")
            client = USASpendingClient()
            result = client.search_dhs_contracts(fiscal_year=2024, keyword="detention")
            print(f"Found {len(result)} detention contracts")

    else:
        print("Usage: python data_ingestion.py [ingest|analyze|test]")
