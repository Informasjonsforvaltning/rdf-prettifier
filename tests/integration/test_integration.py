"""Integration tests."""

from random import randrange
from textwrap import dedent

from fastapi import Response
from fastapi.responses import PlainTextResponse
import pytest

from rdf_diff_store.main import delete_api_graphs, get_api_graphs, post_api_graphs
from rdf_diff_store.models import Graph, ID, Message, TemporalID


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
    r = Response()
    assert post_api_graphs(graph, r) is None
    assert r.status_code == 200


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
    r = Response()
    assert post_api_graphs(graph, r) is None
    assert r.status_code == 200

    update = Graph(
        id=graph_id,
        graph="""
        @prefix si: <https://www.w3schools.com/rdf/> .

        <https://www.w3schools.com> si:author "John Doe" ;
            si:title "W3Schools" .
        """,
    )
    r = Response()
    assert post_api_graphs(update, r) is None
    assert r.status_code == 200

    body = TemporalID(
        id=graph_id,
    )
    r = Response()
    response = get_api_graphs(body, r)
    assert r.status_code == 200
    assert isinstance(response, PlainTextResponse)
    assert response.body.decode("utf-8") == dedent(update.graph).strip()


@pytest.mark.integration
def test_delete() -> None:
    """Delete graph."""
    graph_id = str(randrange(100000, 1000000))
    graph = Graph(
        id=graph_id,
        graph="""
        @prefix si: <https://www.w3schools.com/rdf/> .

        <https://www.w3schools.com> si:author "Jan Egil Refsnes" ;
            si:title "W3Schools" .
        """,
    )
    r = Response()
    assert post_api_graphs(graph, r) is None
    assert r.status_code == 200

    tid = TemporalID(
        id=graph_id,
    )
    r = Response()
    response = get_api_graphs(tid, r)
    assert r.status_code == 200
    assert isinstance(response, PlainTextResponse)
    assert response.body.decode("utf-8") == dedent(graph.graph).strip()

    id = ID(
        id=graph_id,
    )
    r = Response()
    assert delete_api_graphs(id, r) is None
    assert r.status_code == 200

    r = Response()
    response = get_api_graphs(tid, r)
    assert r.status_code == 404
    assert isinstance(response, Message)
    assert response == Message(message=f"No such graph: '{graph_id}'")


@pytest.mark.integration
def test_delete_nonexisting() -> None:
    """Delete graph that does not exist."""
    graph_id = str(randrange(100000, 1000000))
    id = ID(
        id=graph_id,
    )
    r = Response()
    response = delete_api_graphs(id, r)
    assert r.status_code == 404
    assert isinstance(response, Message)
    assert response == Message(message=f"No such graph: '{graph_id}'")
