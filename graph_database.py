"""
Project Watchtower - Graph Database Module
INFRA: Neo4j integration with NetworkX fallback

Provides graph database functionality for network analysis,
with graceful degradation to in-memory NetworkX when Neo4j
is not available.
"""

import os
import networkx as nx
from typing import Dict, List, Optional, Any
import json

# Try to import Neo4j driver
try:
    from neo4j import GraphDatabase
    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False


class GraphDB:
    """
    Graph database abstraction layer.

    Uses Neo4j when available, falls back to NetworkX for
    local development and testing.
    """

    def __init__(self):
        self.neo4j_uri = os.environ.get('NEO4J_URI')
        self.neo4j_user = os.environ.get('NEO4J_USER', 'neo4j')
        self.neo4j_password = os.environ.get('NEO4J_PASSWORD')

        self._driver = None
        self._graph = nx.DiGraph()  # Fallback graph

        if NEO4J_AVAILABLE and self.neo4j_uri and self.neo4j_password:
            try:
                self._driver = GraphDatabase.driver(
                    self.neo4j_uri,
                    auth=(self.neo4j_user, self.neo4j_password)
                )
                # Test connection
                with self._driver.session() as session:
                    session.run("RETURN 1")
                print("Connected to Neo4j")
            except Exception as e:
                print(f"Neo4j connection failed, using NetworkX fallback: {e}")
                self._driver = None
        else:
            print("Neo4j not configured, using NetworkX fallback")

    @property
    def using_neo4j(self) -> bool:
        """Check if using Neo4j or fallback."""
        return self._driver is not None

    def close(self):
        """Close database connection."""
        if self._driver:
            self._driver.close()

    # Node operations
    def add_node(self, node_id: str, label: str, properties: Dict[str, Any] = None):
        """Add a node to the graph."""
        props = properties or {}

        if self._driver:
            with self._driver.session() as session:
                query = f"""
                MERGE (n:{label} {{id: $node_id}})
                SET n += $props
                RETURN n
                """
                session.run(query, node_id=node_id, props=props)
        else:
            self._graph.add_node(node_id, label=label, **props)

    def get_node(self, node_id: str) -> Optional[Dict]:
        """Get a node by ID."""
        if self._driver:
            with self._driver.session() as session:
                result = session.run(
                    "MATCH (n {id: $node_id}) RETURN n",
                    node_id=node_id
                )
                record = result.single()
                if record:
                    return dict(record['n'])
                return None
        else:
            if node_id in self._graph.nodes:
                return dict(self._graph.nodes[node_id])
            return None

    def get_nodes_by_label(self, label: str) -> List[Dict]:
        """Get all nodes with a specific label."""
        if self._driver:
            with self._driver.session() as session:
                result = session.run(f"MATCH (n:{label}) RETURN n")
                return [dict(record['n']) for record in result]
        else:
            return [
                {'id': n, **data}
                for n, data in self._graph.nodes(data=True)
                if data.get('label') == label
            ]

    # Edge operations
    def add_edge(self, from_id: str, to_id: str, rel_type: str,
                 properties: Dict[str, Any] = None):
        """Add an edge/relationship to the graph."""
        props = properties or {}

        if self._driver:
            with self._driver.session() as session:
                query = f"""
                MATCH (a {{id: $from_id}}), (b {{id: $to_id}})
                MERGE (a)-[r:{rel_type}]->(b)
                SET r += $props
                RETURN r
                """
                session.run(query, from_id=from_id, to_id=to_id, props=props)
        else:
            self._graph.add_edge(from_id, to_id, rel_type=rel_type, **props)

    def get_edges(self, node_id: str, direction: str = 'both') -> List[Dict]:
        """Get edges connected to a node."""
        edges = []

        if self._driver:
            with self._driver.session() as session:
                if direction in ('out', 'both'):
                    result = session.run(
                        "MATCH (n {id: $node_id})-[r]->(m) RETURN type(r) as type, m.id as target, r",
                        node_id=node_id
                    )
                    edges.extend([{
                        'source': node_id,
                        'target': r['target'],
                        'type': r['type'],
                        **dict(r['r'])
                    } for r in result])

                if direction in ('in', 'both'):
                    result = session.run(
                        "MATCH (n {id: $node_id})<-[r]-(m) RETURN type(r) as type, m.id as source, r",
                        node_id=node_id
                    )
                    edges.extend([{
                        'source': r['source'],
                        'target': node_id,
                        'type': r['type'],
                        **dict(r['r'])
                    } for r in result])
        else:
            if direction in ('out', 'both'):
                for _, target, data in self._graph.out_edges(node_id, data=True):
                    edges.append({
                        'source': node_id,
                        'target': target,
                        **data
                    })
            if direction in ('in', 'both'):
                for source, _, data in self._graph.in_edges(node_id, data=True):
                    edges.append({
                        'source': source,
                        'target': node_id,
                        **data
                    })

        return edges

    # Query operations
    def find_path(self, from_id: str, to_id: str, max_depth: int = 5) -> List[str]:
        """Find shortest path between two nodes."""
        if self._driver:
            with self._driver.session() as session:
                result = session.run(f"""
                    MATCH path = shortestPath(
                        (a {{id: $from_id}})-[*..{max_depth}]-(b {{id: $to_id}})
                    )
                    RETURN [n in nodes(path) | n.id] as path
                """, from_id=from_id, to_id=to_id)
                record = result.single()
                if record:
                    return record['path']
                return []
        else:
            try:
                return nx.shortest_path(self._graph.to_undirected(), from_id, to_id)
            except (nx.NetworkXNoPath, nx.NodeNotFound):
                return []

    def get_connected_component(self, node_id: str) -> List[str]:
        """Get all nodes in the same connected component."""
        if self._driver:
            with self._driver.session() as session:
                result = session.run("""
                    MATCH (start {id: $node_id})
                    CALL apoc.path.subgraphNodes(start, {maxLevel: 10}) YIELD node
                    RETURN node.id as id
                """, node_id=node_id)
                return [r['id'] for r in result]
        else:
            undirected = self._graph.to_undirected()
            if node_id in undirected:
                return list(nx.node_connected_component(undirected, node_id))
            return []

    def get_centrality(self, measure: str = 'degree') -> Dict[str, float]:
        """Calculate centrality measures for all nodes."""
        if self._driver:
            # For Neo4j, we'd use Graph Data Science library
            # Fallback to exporting to NetworkX for calculation
            with self._driver.session() as session:
                result = session.run("MATCH (n) RETURN n.id as id")
                nodes = [r['id'] for r in result]
                result = session.run("MATCH (a)-[r]->(b) RETURN a.id as source, b.id as target")
                edges = [(r['source'], r['target']) for r in result]

            G = nx.DiGraph()
            G.add_nodes_from(nodes)
            G.add_edges_from(edges)
        else:
            G = self._graph

        if measure == 'degree':
            return dict(nx.degree_centrality(G))
        elif measure == 'betweenness':
            return dict(nx.betweenness_centrality(G))
        elif measure == 'pagerank':
            return dict(nx.pagerank(G))
        else:
            return dict(nx.degree_centrality(G))

    # Bulk operations
    def load_from_dict(self, data: Dict):
        """Load graph from dictionary format."""
        for node in data.get('nodes', []):
            self.add_node(
                node['id'],
                node.get('label', 'Node'),
                {k: v for k, v in node.items() if k not in ('id', 'label')}
            )

        for edge in data.get('edges', []):
            self.add_edge(
                edge['source'],
                edge['target'],
                edge.get('type', 'CONNECTED'),
                {k: v for k, v in edge.items() if k not in ('source', 'target', 'type')}
            )

    def export_to_dict(self) -> Dict:
        """Export graph to dictionary format."""
        if self._driver:
            with self._driver.session() as session:
                nodes_result = session.run("MATCH (n) RETURN n")
                nodes = [{'id': dict(r['n']).get('id'), **dict(r['n'])} for r in nodes_result]

                edges_result = session.run(
                    "MATCH (a)-[r]->(b) RETURN a.id as source, b.id as target, type(r) as type, r"
                )
                edges = [{
                    'source': r['source'],
                    'target': r['target'],
                    'type': r['type'],
                    **dict(r['r'])
                } for r in edges_result]
        else:
            nodes = [{'id': n, **data} for n, data in self._graph.nodes(data=True)]
            edges = [{
                'source': u,
                'target': v,
                **data
            } for u, v, data in self._graph.edges(data=True)]

        return {'nodes': nodes, 'edges': edges}

    def get_networkx_graph(self) -> nx.DiGraph:
        """Get NetworkX graph object for visualization."""
        if self._driver:
            G = nx.DiGraph()
            data = self.export_to_dict()
            for node in data['nodes']:
                G.add_node(node['id'], **{k: v for k, v in node.items() if k != 'id'})
            for edge in data['edges']:
                G.add_edge(edge['source'], edge['target'],
                          **{k: v for k, v in edge.items() if k not in ('source', 'target')})
            return G
        else:
            return self._graph.copy()


# Singleton instance
_graph_db = None

def get_graph_db() -> GraphDB:
    """Get the graph database instance."""
    global _graph_db
    if _graph_db is None:
        _graph_db = GraphDB()
    return _graph_db


def init_graph_schema():
    """Initialize graph database schema/indexes."""
    db = get_graph_db()

    if db.using_neo4j:
        with db._driver.session() as session:
            # Create indexes
            session.run("CREATE INDEX IF NOT EXISTS FOR (p:Person) ON (p.id)")
            session.run("CREATE INDEX IF NOT EXISTS FOR (o:Organization) ON (o.id)")
            session.run("CREATE INDEX IF NOT EXISTS FOR (p:Position) ON (p.id)")
            session.run("CREATE INDEX IF NOT EXISTS FOR (c:Contract) ON (c.id)")
            print("Neo4j schema initialized")
    else:
        print("Using NetworkX fallback - no schema needed")
