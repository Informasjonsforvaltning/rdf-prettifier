"""SparQL."""

from typing import Optional

from rdf_diff_store.rdf import parse_all_graphs


async def query_sparql(query: str, timestamp: Optional[int] = None) -> str:
    """Query SparQL."""
    g = await parse_all_graphs(timestamp)

    result = g.query(query).serialize(format="json")
    if result:
        return result.decode("utf-8")
    return ""
