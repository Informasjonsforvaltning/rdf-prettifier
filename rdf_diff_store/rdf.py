"""RDF."""

from typing import Union

from rdflib import Graph


def to_turtle(graph: str, format: Union[None, str]) -> str:
    """Convert graph to turtle format."""
    # graph.strip() can fix invalid xml format (leading newline)
    g = Graph().parse(data=graph.strip(), format=format)
    return g.serialize(format="text/turtle").strip()
