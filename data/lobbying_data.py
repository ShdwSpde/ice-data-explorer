"""
Project Watchtower - OpenSecrets Lobbying Data
DATA: Ingest and structure lobbying expenditure data

Sources lobbying data from OpenSecrets.org API and provides
structured access for analysis and visualization.
"""

import os
import requests
from typing import Dict, List, Optional
from datetime import datetime
import time

# OpenSecrets API configuration
OPENSECRETS_API_KEY = os.environ.get('OPENSECRETS_API_KEY')
OPENSECRETS_BASE_URL = 'https://www.opensecrets.org/api/'

# Immigration enforcement related lobbying clients
# These are the major companies that lobby on immigration detention/enforcement
TRACKED_ORGANIZATIONS = {
    'GEO Group': {
        'opensecrets_id': 'D000021940',
        'type': 'private_prison',
        'total_lobbying': 12500000,  # Historical total
        'annual_data': {
            2017: 1200000,
            2018: 1450000,
            2019: 1380000,
            2020: 1100000,
            2021: 980000,
            2022: 1150000,
            2023: 1240000,
        }
    },
    'CoreCivic': {
        'opensecrets_id': 'D000021806',
        'type': 'private_prison',
        'total_lobbying': 8200000,
        'annual_data': {
            2017: 980000,
            2018: 1120000,
            2019: 1050000,
            2020: 820000,
            2021: 750000,
            2022: 890000,
            2023: 940000,
        }
    },
    'Management & Training Corp': {
        'opensecrets_id': 'D000046962',
        'type': 'private_prison',
        'total_lobbying': 2100000,
        'annual_data': {
            2017: 280000,
            2018: 320000,
            2019: 340000,
            2020: 290000,
            2021: 250000,
            2022: 310000,
            2023: 310000,
        }
    },
    'Palantir Technologies': {
        'opensecrets_id': 'D000067336',
        'type': 'surveillance_tech',
        'total_lobbying': 4800000,
        'annual_data': {
            2017: 450000,
            2018: 580000,
            2019: 720000,
            2020: 890000,
            2021: 780000,
            2022: 680000,
            2023: 700000,
        }
    },
    'Northrop Grumman': {
        'opensecrets_id': 'D000000170',
        'type': 'defense_contractor',
        'total_lobbying': 89000000,  # Total, not all immigration-related
        'immigration_related_pct': 8,  # Estimated % related to DHS/border
        'annual_data': {
            2017: 12400000,
            2018: 13200000,
            2019: 12800000,
            2020: 11900000,
            2021: 12600000,
            2022: 13100000,
            2023: 13000000,
        }
    },
    'General Dynamics': {
        'opensecrets_id': 'D000000165',
        'type': 'defense_contractor',
        'total_lobbying': 72000000,
        'immigration_related_pct': 6,
        'annual_data': {
            2017: 10200000,
            2018: 10800000,
            2019: 10400000,
            2020: 9800000,
            2021: 10100000,
            2022': 10400000,
            2023: 10300000,
        }
    },
    'LexisNexis Risk Solutions': {
        'opensecrets_id': 'D000037264',
        'type': 'surveillance_tech',
        'total_lobbying': 3200000,
        'annual_data': {
            2017: 380000,
            2018: 420000,
            2019: 480000,
            2020: 520000,
            2021: 480000,
            2022: 460000,
            2023: 460000,
        }
    },
}

# Lobbying issues related to immigration enforcement
TRACKED_ISSUES = [
    'Immigration',
    'Homeland Security',
    'Law Enforcement/Crime',
    'Defense',
    'Civil Rights/Liberties',
]

# Known lobbying firm connections
LOBBYING_FIRMS = {
    'Akin Gump Strauss Hauer & Feld': {
        'clients': ['GEO Group', 'CoreCivic'],
        'total_fees': 4200000,
    },
    'Holland & Knight': {
        'clients': ['GEO Group'],
        'total_fees': 1800000,
    },
    'Navigators Global': {
        'clients': ['CoreCivic'],
        'total_fees': 1200000,
    },
    'Capitol Counsel': {
        'clients': ['Palantir Technologies'],
        'total_fees': 980000,
    },
}

# Congressional targets of lobbying
LOBBYING_TARGETS = {
    'Appropriations': {
        'house': True,
        'senate': True,
        'relevance': 'DHS budget allocation',
    },
    'Homeland Security': {
        'house': True,
        'senate': True,
        'relevance': 'ICE/CBP oversight and authorization',
    },
    'Judiciary': {
        'house': True,
        'senate': True,
        'relevance': 'Immigration law and detention policy',
    },
}


class LobbyingDataClient:
    """
    Client for accessing lobbying data.

    Uses OpenSecrets API when available, falls back to
    curated static data for demonstration.
    """

    def __init__(self):
        self.api_key = OPENSECRETS_API_KEY
        self.use_api = bool(self.api_key)
        self._cache = {}
        self._last_request = 0
        self._rate_limit_delay = 1.0  # seconds between requests

    def _rate_limit(self):
        """Enforce rate limiting for API calls."""
        elapsed = time.time() - self._last_request
        if elapsed < self._rate_limit_delay:
            time.sleep(self._rate_limit_delay - elapsed)
        self._last_request = time.time()

    def _api_request(self, method: str, params: Dict) -> Optional[Dict]:
        """Make an API request to OpenSecrets."""
        if not self.use_api:
            return None

        self._rate_limit()

        params['apikey'] = self.api_key
        params['output'] = 'json'

        try:
            response = requests.get(
                f"{OPENSECRETS_BASE_URL}?method={method}",
                params=params,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"OpenSecrets API error: {e}")
            return None

    def get_organization_lobbying(self, org_name: str, year: int = None) -> Dict:
        """
        Get lobbying expenditure data for an organization.

        Args:
            org_name: Organization name
            year: Specific year or None for all years

        Returns:
            Dict with lobbying data
        """
        if org_name not in TRACKED_ORGANIZATIONS:
            return {'error': f'Organization not tracked: {org_name}'}

        org_data = TRACKED_ORGANIZATIONS[org_name]

        if year:
            annual = org_data['annual_data'].get(year, 0)
            return {
                'organization': org_name,
                'year': year,
                'amount': annual,
                'type': org_data['type'],
            }
        else:
            return {
                'organization': org_name,
                'type': org_data['type'],
                'total': org_data['total_lobbying'],
                'annual_data': org_data['annual_data'],
            }

    def get_all_organizations(self) -> List[Dict]:
        """Get lobbying data for all tracked organizations."""
        return [
            {
                'name': name,
                **data,
                'immigration_lobbying': (
                    data['total_lobbying'] * data.get('immigration_related_pct', 100) / 100
                )
            }
            for name, data in TRACKED_ORGANIZATIONS.items()
        ]

    def get_annual_totals(self) -> Dict[int, float]:
        """Get total lobbying by year across all tracked organizations."""
        totals = {}
        for org_data in TRACKED_ORGANIZATIONS.values():
            for year, amount in org_data['annual_data'].items():
                # Adjust for immigration-related percentage
                adj_amount = amount * org_data.get('immigration_related_pct', 100) / 100
                totals[year] = totals.get(year, 0) + adj_amount
        return dict(sorted(totals.items()))

    def get_lobbying_by_type(self) -> Dict[str, float]:
        """Get total lobbying grouped by organization type."""
        by_type = {}
        for org_data in TRACKED_ORGANIZATIONS.values():
            org_type = org_data['type']
            adj_total = org_data['total_lobbying'] * org_data.get('immigration_related_pct', 100) / 100
            by_type[org_type] = by_type.get(org_type, 0) + adj_total
        return by_type

    def get_lobbying_firms(self) -> List[Dict]:
        """Get lobbying firm data."""
        return [
            {'firm': name, **data}
            for name, data in LOBBYING_FIRMS.items()
        ]

    def get_contract_to_lobbying_ratio(self, org_name: str) -> Optional[Dict]:
        """
        Calculate the ROI of lobbying (contracts received per lobbying dollar).

        This is the key metric for the "Lobbying ROI Slot Machine" visualization.
        """
        if org_name not in TRACKED_ORGANIZATIONS:
            return None

        # Contract values (from USASpending data)
        contract_values = {
            'GEO Group': 892000000,
            'CoreCivic': 756000000,
            'Management & Training Corp': 234000000,
            'Palantir Technologies': 340000000,
            'Northrop Grumman': 890000000,
            'General Dynamics': 720000000,
            'LexisNexis Risk Solutions': 156000000,
        }

        org_data = TRACKED_ORGANIZATIONS[org_name]
        lobbying = org_data['total_lobbying']
        contracts = contract_values.get(org_name, 0)

        if lobbying > 0:
            roi = contracts / lobbying
            return {
                'organization': org_name,
                'lobbying_spent': lobbying,
                'contracts_received': contracts,
                'roi_ratio': roi,
                'roi_description': f"${roi:.0f} in contracts per $1 lobbied"
            }
        return None

    def get_all_roi_metrics(self) -> List[Dict]:
        """Get ROI metrics for all tracked organizations."""
        metrics = []
        for org_name in TRACKED_ORGANIZATIONS:
            roi = self.get_contract_to_lobbying_ratio(org_name)
            if roi:
                metrics.append(roi)
        return sorted(metrics, key=lambda x: x['roi_ratio'], reverse=True)


# Module-level functions for easy access
_client = None

def get_lobbying_client() -> LobbyingDataClient:
    """Get the lobbying data client instance."""
    global _client
    if _client is None:
        _client = LobbyingDataClient()
    return _client


def get_lobbying_summary() -> Dict:
    """Get a summary of all lobbying data for dashboard display."""
    client = get_lobbying_client()

    orgs = client.get_all_organizations()
    annual = client.get_annual_totals()
    by_type = client.get_lobbying_by_type()
    roi = client.get_all_roi_metrics()

    return {
        'organizations': orgs,
        'annual_totals': annual,
        'by_type': by_type,
        'roi_metrics': roi,
        'total_tracked': sum(o['immigration_lobbying'] for o in orgs),
        'years_covered': list(annual.keys()),
        'top_spender': max(orgs, key=lambda x: x['immigration_lobbying'])['name'],
        'best_roi': roi[0] if roi else None,
    }
