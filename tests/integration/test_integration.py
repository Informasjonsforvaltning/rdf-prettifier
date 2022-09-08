"""Integration tests."""

from random import randrange
from textwrap import dedent

import pytest

from rdf_diff_store.main import get_api_graphs, post_api_graphs
from rdf_diff_store.models import Graph, TemporalID


@pytest.mark.integration
def test_store_turtle() -> None:
    """Store graph."""
    graph_id = str(randrange(100000, 1000000))
    graph = Graph(
        id=graph_id,
        graph="""
        @prefix si: <https://www.w3schools.com/rdf/> .

        <https://www.w3schools.com> si:author "Jan Egil Refsnes" ;
            si:title "W3Schools" .
        """,
    )
    assert post_api_graphs(graph) is None


@pytest.mark.integration
def test_update() -> None:
    """Update graph."""
    graph_id = str(randrange(100000, 1000000))
    graph = Graph(
        id=graph_id,
        graph="""
        @prefix si: <https://www.w3schools.com/rdf/> .

        <https://www.w3schools.com> si:author "Jan Egil Refsnes" ;
            si:title "W3Schools" .
        """,
    )
    assert post_api_graphs(graph) is None

    update = Graph(
        id=graph_id,
        graph="""
        @prefix si: <https://www.w3schools.com/rdf/> .

        <https://www.w3schools.com> si:author "John Doe" ;
            si:title "W3Schools" .
        """,
    )
    assert post_api_graphs(update) is None

    body = TemporalID(
        id=graph_id,
    )
    assert get_api_graphs(body).body.decode("utf-8") == dedent(update.graph).strip()
