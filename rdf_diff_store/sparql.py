"""SparQL."""

from typing import Optional

from rdflib import Graph

from .git import load_all_graphs


def query_sparql(query: str, timestamp: Optional[int] = None) -> str:
    """Query SparQL."""
    g = Graph()

    for graph in load_all_graphs(timestamp):
        g.parse(data=graph)

    result = g.query(query).serialize(format="json")
    if result:
        return result.decode("utf-8")
    return ""
