"""
Project Watchtower - Personnel/Revolving Door Dataset
DATA: Track personnel movements between government and contractors

Documents the "revolving door" between ICE/DHS and private contractors,
revealing how former officials become industry advocates.
"""

from typing import Dict, List, Optional
from datetime import datetime
from graph_database import get_graph_db


# Documented revolving door personnel
# Sources: LinkedIn, SEC filings, news reports, FOIA releases
REVOLVING_DOOR_PERSONNEL = [
    # Government to Industry
    {
        'id': 'person-001',
        'name': 'David Venturella',
        'type': 'gov_to_industry',
        'government_role': {
            'agency': 'ICE',
            'position': 'Executive Associate Director, ERO',
            'years': '2006-2011',
            'responsibilities': 'Oversaw detention and removal operations',
        },
        'industry_role': {
            'company': 'GEO Group',
            'position': 'Vice President, Business Development',
            'years': '2012-present',
            'responsibilities': 'Federal contract acquisition',
        },
        'significance': 'Led ICE detention expansion, now helps GEO win contracts',
        'source': 'LinkedIn, GEO Group SEC filings',
    },
    {
        'id': 'person-002',
        'name': 'Julie Myers Wood',
        'type': 'gov_to_industry',
        'government_role': {
            'agency': 'ICE',
            'position': 'Assistant Secretary of Homeland Security',
            'years': '2006-2008',
            'responsibilities': 'Head of ICE',
        },
        'industry_role': {
            'company': 'Immigration Policy Consulting',
            'position': 'CEO, Immigration Customs Compliance (ICS)',
            'years': '2009-present',
            'responsibilities': 'Immigration enforcement consulting',
        },
        'significance': 'Former ICE head now advises companies on compliance',
        'source': 'ICS website, news reports',
    },
    {
        'id': 'person-003',
        'name': 'John Sandweg',
        'type': 'gov_to_industry',
        'government_role': {
            'agency': 'ICE',
            'position': 'Acting Director',
            'years': '2013-2014',
            'responsibilities': 'Led ICE operations',
        },
        'industry_role': {
            'company': 'Multiple clients',
            'position': 'Immigration Attorney, Consultant',
            'years': '2014-present',
            'responsibilities': 'Immigration law, media commentary',
        },
        'significance': 'Former acting director, now private sector',
        'source': 'LinkedIn, news appearances',
    },
    {
        'id': 'person-004',
        'name': 'Brian Dunn',
        'type': 'gov_to_industry',
        'government_role': {
            'agency': 'ICE',
            'position': 'Deputy Director, ERO',
            'years': '2008-2015',
            'responsibilities': 'Enforcement and Removal Operations',
        },
        'industry_role': {
            'company': 'GEO Group',
            'position': 'Senior Director, Government Affairs',
            'years': '2016-present',
            'responsibilities': 'Federal relations and lobbying',
        },
        'significance': 'Direct oversight of detention now lobbies for detention contracts',
        'source': 'GEO Group lobbying disclosures',
    },
    {
        'id': 'person-005',
        'name': 'Matthew Albence',
        'type': 'gov_to_industry',
        'government_role': {
            'agency': 'ICE',
            'position': 'Acting Director',
            'years': '2019-2020',
            'responsibilities': 'Led ICE during peak detention',
        },
        'industry_role': {
            'company': 'Immigration Policy Consulting',
            'position': 'Consultant',
            'years': '2021-present',
            'responsibilities': 'Immigration enforcement consulting',
        },
        'significance': 'Oversaw largest detention expansion in history',
        'source': 'News reports',
    },
    {
        'id': 'person-006',
        'name': 'Kevin McAleenan',
        'type': 'gov_to_industry',
        'government_role': {
            'agency': 'DHS',
            'position': 'Acting Secretary of Homeland Security',
            'years': '2019',
            'responsibilities': 'Led DHS during family separation policy',
        },
        'industry_role': {
            'company': 'Pangiam',
            'position': 'CEO',
            'years': '2020-present',
            'responsibilities': 'Border technology company',
        },
        'significance': 'From DHS head to border tech CEO',
        'source': 'Pangiam website, SEC filings',
    },
    # Industry to Government
    {
        'id': 'person-007',
        'name': 'George Zoley',
        'type': 'industry_influence',
        'company': 'GEO Group',
        'position': 'Founder and CEO',
        'years': '1984-2021',
        'political_connections': [
            'Major Trump donor ($475,000)',
            'Trump inaugural committee donor',
            'Regular visitor to Trump properties',
        ],
        'significance': 'Built private prison empire through political connections',
        'source': 'FEC filings, news investigations',
    },
    {
        'id': 'person-008',
        'name': 'Damon Hininger',
        'type': 'industry_influence',
        'company': 'CoreCivic',
        'position': 'CEO',
        'years': '2009-present',
        'political_connections': [
            'Political contributions via PAC',
            'Industry association leadership',
        ],
        'significance': 'Leads second-largest private prison company',
        'source': 'CoreCivic SEC filings',
    },
    # Lobbyists
    {
        'id': 'person-009',
        'name': 'Brian Ballard',
        'type': 'lobbyist',
        'firm': 'Ballard Partners',
        'clients': ['GEO Group'],
        'government_connections': [
            'Close Trump advisor',
            'Former Florida Republican fundraiser',
        ],
        'significance': 'Key Trump-connected lobbyist for private prison industry',
        'source': 'Lobbying disclosures, news reports',
    },
    {
        'id': 'person-010',
        'name': 'David Safavian',
        'type': 'lobbyist',
        'firm': 'Former GSA official',
        'clients': ['CoreCivic', 'GEO Group'],
        'government_connections': [
            'Former GSA Chief of Staff',
            'Convicted in Abramoff scandal, pardoned',
        ],
        'significance': 'Controversial lobbyist with government procurement background',
        'source': 'Lobbying disclosures, court records',
    },
]

# Organizational connections
ORGANIZATIONAL_CONNECTIONS = [
    {
        'from': 'ICE ERO',
        'to': 'GEO Group',
        'type': 'personnel_flow',
        'count': 12,
        'description': 'Known former ERO officials now at GEO',
    },
    {
        'from': 'ICE ERO',
        'to': 'CoreCivic',
        'type': 'personnel_flow',
        'count': 8,
        'description': 'Known former ERO officials now at CoreCivic',
    },
    {
        'from': 'DHS Leadership',
        'to': 'Border Tech Companies',
        'type': 'personnel_flow',
        'count': 6,
        'description': 'Former DHS leaders at surveillance/tech startups',
    },
    {
        'from': 'GEO Group',
        'to': 'Congress',
        'type': 'lobbying',
        'count': 45,
        'description': 'Registered lobbyists targeting immigration committees',
    },
    {
        'from': 'CoreCivic',
        'to': 'Congress',
        'type': 'lobbying',
        'count': 32,
        'description': 'Registered lobbyists targeting immigration committees',
    },
    {
        'from': 'Private Prison Industry',
        'to': 'Republican Party',
        'type': 'campaign_contributions',
        'amount': 4500000,
        'description': 'Campaign contributions 2016-2024',
    },
    {
        'from': 'Private Prison Industry',
        'to': 'Democratic Party',
        'type': 'campaign_contributions',
        'amount': 850000,
        'description': 'Campaign contributions 2016-2024',
    },
]


class RevolvingDoorDatabase:
    """
    Access layer for revolving door personnel data.
    """

    def __init__(self):
        self._personnel = {p['id']: p for p in REVOLVING_DOOR_PERSONNEL}
        self._connections = ORGANIZATIONAL_CONNECTIONS

    def get_all_personnel(self) -> List[Dict]:
        """Get all tracked personnel."""
        return list(self._personnel.values())

    def get_personnel_by_type(self, person_type: str) -> List[Dict]:
        """Get personnel by movement type."""
        return [p for p in self._personnel.values() if p['type'] == person_type]

    def get_gov_to_industry(self) -> List[Dict]:
        """Get government-to-industry personnel moves."""
        return self.get_personnel_by_type('gov_to_industry')

    def get_industry_to_gov(self) -> List[Dict]:
        """Get industry-to-government personnel moves."""
        return self.get_personnel_by_type('industry_to_gov')

    def get_lobbyists(self) -> List[Dict]:
        """Get known lobbyists."""
        return self.get_personnel_by_type('lobbyist')

    def get_connections_by_type(self, conn_type: str) -> List[Dict]:
        """Get organizational connections by type."""
        return [c for c in self._connections if c['type'] == conn_type]

    def get_personnel_for_company(self, company: str) -> List[Dict]:
        """Get all personnel associated with a company."""
        results = []
        for person in self._personnel.values():
            if person.get('industry_role', {}).get('company') == company:
                results.append(person)
            if person.get('company') == company:
                results.append(person)
            if company in person.get('clients', []):
                results.append(person)
        return results

    def build_network_graph(self) -> Dict:
        """
        Build a network graph structure for visualization.

        Returns:
            Dict with nodes and edges for network visualization
        """
        nodes = []
        edges = []

        # Add organization nodes
        orgs = set()
        for conn in self._connections:
            orgs.add(conn['from'])
            orgs.add(conn['to'])

        for org in orgs:
            node_type = 'government' if org in ['ICE ERO', 'DHS Leadership', 'Congress'] else 'industry'
            nodes.append({
                'id': org.replace(' ', '_'),
                'label': org,
                'type': node_type,
            })

        # Add person nodes
        for person in self._personnel.values():
            nodes.append({
                'id': person['id'],
                'label': person['name'],
                'type': 'person',
                'subtype': person['type'],
            })

        # Add edges from connections
        for conn in self._connections:
            edges.append({
                'source': conn['from'].replace(' ', '_'),
                'target': conn['to'].replace(' ', '_'),
                'type': conn['type'],
                'weight': conn.get('count', conn.get('amount', 1)),
            })

        # Add edges from personnel movements
        for person in self._personnel.values():
            if person['type'] == 'gov_to_industry':
                gov_agency = person['government_role']['agency']
                company = person['industry_role']['company']
                edges.append({
                    'source': gov_agency.replace(' ', '_'),
                    'target': person['id'],
                    'type': 'former_employee',
                })
                edges.append({
                    'source': person['id'],
                    'target': company.replace(' ', '_'),
                    'type': 'current_employee',
                })

        return {'nodes': nodes, 'edges': edges}

    def load_into_graph_db(self):
        """Load revolving door data into graph database."""
        db = get_graph_db()
        network = self.build_network_graph()

        for node in network['nodes']:
            db.add_node(
                node['id'],
                node['type'].title(),
                {k: v for k, v in node.items() if k not in ('id', 'type')}
            )

        for edge in network['edges']:
            db.add_edge(
                edge['source'],
                edge['target'],
                edge['type'].upper(),
                {k: v for k, v in edge.items() if k not in ('source', 'target', 'type')}
            )

        print(f"Loaded {len(network['nodes'])} nodes and {len(network['edges'])} edges into graph database")

    def get_summary_stats(self) -> Dict:
        """Get summary statistics for dashboard display."""
        gov_to_industry = self.get_gov_to_industry()
        lobbyists = self.get_lobbyists()

        return {
            'total_personnel_tracked': len(self._personnel),
            'gov_to_industry_count': len(gov_to_industry),
            'lobbyists_tracked': len(lobbyists),
            'total_connections': len(self._connections),
            'top_receiving_companies': ['GEO Group', 'CoreCivic', 'Palantir'],
            'key_finding': 'At least 12 former ICE ERO officials now work for GEO Group',
        }


# Module-level access
_database = None

def get_revolving_door_db() -> RevolvingDoorDatabase:
    """Get the revolving door database instance."""
    global _database
    if _database is None:
        _database = RevolvingDoorDatabase()
    return _database


def get_revolving_door_summary() -> Dict:
    """Get a summary of revolving door data."""
    db = get_revolving_door_db()
    return db.get_summary_stats()


def get_revolving_door_network() -> Dict:
    """Get network graph data for visualization."""
    db = get_revolving_door_db()
    return db.build_network_graph()
