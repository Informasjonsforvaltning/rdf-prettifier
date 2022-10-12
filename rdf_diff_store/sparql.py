"""SparQL."""

from typing import Optional

from rdflib import Graph

from .git import iterate_all_graphs


async def query_sparql(query: str, timestamp: Optional[int] = None) -> str:
    """Query SparQL."""
    g = Graph()

    async for graph in iterate_all_graphs(timestamp):
        g.parse(data=graph)

    result = g.query(query).serialize(format="json")
    if result:
        return result.decode("utf-8")
    return ""
