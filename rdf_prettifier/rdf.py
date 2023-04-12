"""RDF."""

from typing import Union

from rdflib import Graph


def prettify(
    graph: str, input_format: Union[None, str], output_format: Union[None, str]
) -> str:
    """Convert graph to specified format and prettify."""
    if output_format is None:
        output_format = "ttl"
    # graph.strip() can fix invalid xml format (leading newline)
    g = Graph().parse(data=graph.strip(), format=input_format)
    return g.serialize(format=output_format).strip()
