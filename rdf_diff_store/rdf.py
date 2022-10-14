"""RDF."""

from typing import Optional, Union

from rdf_diff_store.git import iterate_all_graphs

from rdflib import Graph


def to_turtle(graph: str, format: Union[None, str]) -> str:
    """Convert graph to turtle format."""
    # graph.strip() can fix invalid xml format (leading newline)
    g = Graph().parse(data=graph.strip(), format=format)
    return g.serialize(format="text/turtle").strip()


async def parse_all_graphs(timestamp: Optional[int]) -> Graph:
    """Parse all graphs."""
    g = Graph()
    async for graph in iterate_all_graphs(timestamp):
        g.parse(data=graph, format="text/turtle")
    return g

async def load_all_graphs_raw(timestamp: Optional[int]) -> str:
    """Load all graphs raw."""
    combined = ""
    async for graph in iterate_all_graphs(timestamp):
        combined += graph + "\n# ---\n"
    return combined


async def load_all_graphs(timestamp: Optional[int]) -> str:
    """Load all graphs."""
    g = await parse_all_graphs(timestamp)
    return g.serialize(format="text/turtle").strip()
