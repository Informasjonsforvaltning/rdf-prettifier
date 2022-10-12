"""RDF."""

from typing import Optional, Union

from rdf_diff_store.git import iterate_all_graphs

from rdflib import Graph


def to_turtle(graph: str, format: Union[None, str]) -> str:
    """Convert graph to turtle format."""
    # graph.strip() can fix invalid xml format (leading newline)
    g = Graph().parse(data=graph.strip(), format=format)
    return g.serialize(format="text/turtle").strip()


async def load_all_graphs(timestamp: Optional[int]) -> str:
    """Load all graphs."""
    g = Graph()
    async for graph in iterate_all_graphs(timestamp):
        g.parse(data=graph)

    return g.serialize(format="text/turtle").strip()
