"""Integration tests."""

from ast import literal_eval
from math import ceil
from random import randrange
from textwrap import dedent
import time
from typing import Any, Dict, List

from fastapi import Response
from fastapi.responses import PlainTextResponse
import pytest

from rdf_diff_store.main import (
    delete_api_graphs,
    get_api_graphs,
    get_api_sparql,
    get_api_sparql_timestamp,
    post_api_graphs,
)
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


@pytest.mark.integration
def test_get_at_timestamp() -> None:
    """Get graph at specific time."""
    graphs = []
    graph_id = str(randrange(1000000, 10000000))

    for i in range(3):
        graph = Graph(
            id=graph_id,
            graph=f"""
            @prefix si: <https://www.w3schools.com/rdf/> .

            <https://www.w3schools.com> si:author "Jan Egil Refsnes" ;
                si:title "W3Schools{i}" .
            """,
        )
        r = Response()
        assert post_api_graphs(graph, r) is None
        assert r.status_code == 200

        graphs.append((graph, time.time()))
        time.sleep(2)

    id = ID(
        id=graph_id,
    )
    r = Response()
    delete_api_graphs(id, r)
    assert r.status_code == 200
    r = Response()
    tid = TemporalID(
        id=graph_id,
    )
    get_api_graphs(tid, r)
    assert r.status_code == 404

    for _i, (graph, t) in enumerate([*graphs, *graphs[::-1]]):
        r = Response()
        tid = TemporalID(id=graph_id, timestamp=t)
        response = get_api_graphs(tid, r)
        assert r.status_code == 200
        assert isinstance(response, PlainTextResponse)
        assert response.body.decode("utf-8") == dedent(graph.graph).strip()

    tid = TemporalID(id=graph_id, timestamp=time.time())
    response = get_api_graphs(tid, r)
    assert r.status_code == 404
    assert isinstance(response, Message)
    assert response == Message(message=f"No such graph: '{graph_id}'")


@pytest.mark.integration
def test_get_sparql() -> None:
    """Test sparql endpoints."""
    node_id = str(randrange(1000000, 10000000))

    # Create a static graph A that is not updated
    graph0 = Graph(
        id=str(randrange(1000000, 10000000)),
        graph=f"""
        @prefix si: <https://www.w3schools.com/rdf/> .

        <https://www.w3schools.com/{node_id}> si:foo "00" ;
            si:bar "007" .
        """,
    )

    r = Response()
    assert post_api_graphs(graph0, r) is None
    assert r.status_code == 200

    # Create v1 of graph B
    graph_id = str(randrange(1000000, 10000000))
    graph1 = Graph(
        id=graph_id,
        graph=f"""
        @prefix si: <https://www.w3schools.com/rdf/> .

        <https://www.w3schools.com/{node_id}> si:foo "Bar" ;
            si:bar "baz" .
        """,
    )
    r = Response()
    assert post_api_graphs(graph1, r) is None
    assert r.status_code == 200

    # Time when graph B is in v1
    t_v1 = ceil(time.time())

    time.sleep(2)

    # Create v2 of graph B
    graph2 = Graph(
        id=graph_id,
        graph=f"""
        @prefix si: <https://www.w3schools.com/rdf/> .

        <https://www.w3schools.com/{node_id}> si:foo "aaaaaaaaaaaaaaaaaaaaaaaaa" ;
            si:bar "bbbbbbbbbbbbbbb" .
        """,
    )
    r = Response()
    assert post_api_graphs(graph2, r) is None
    assert r.status_code == 200

    # Time when graph B is in v2
    t_v2 = ceil(time.time())

    q = f"""SELECT * WHERE {{<https://www.w3schools.com/{node_id}>?pred ?obj .}} LIMIT 10"""

    time.sleep(2)

    # Delete graph B
    id = ID(
        id=graph_id,
    )
    r = Response()
    assert delete_api_graphs(id, r) is None
    assert r.status_code == 200

    # Query without timestamp should yeld A
    r = Response()
    response = get_api_sparql(q, r)
    assert r.status_code == 200
    assert isinstance(response, PlainTextResponse)
    content = literal_eval(response.body.decode("utf-8"))
    expected1: Dict[str, Dict[str, List[Any]]] = {
        "results": {
            "bindings": [
                {
                    "pred": {
                        "type": "uri",
                        "value": "https://www.w3schools.com/rdf/bar",
                    },
                    "obj": {"type": "literal", "value": "007"},
                },
                {
                    "pred": {
                        "type": "uri",
                        "value": "https://www.w3schools.com/rdf/foo",
                    },
                    "obj": {"type": "literal", "value": "00"},
                },
            ]
        },
        "head": {"vars": ["pred", "obj"]},
    }

    assert sorted(content["head"]["vars"]) == sorted(expected1["head"]["vars"])
    assert sorted(
        content["results"]["bindings"], key=lambda a: a["obj"]["value"]
    ) == sorted(expected1["results"]["bindings"], key=lambda a: a["obj"]["value"])

    # Query with timestamp t_v2 should yeld union of A and v2 of B
    r = Response()
    response = get_api_sparql_timestamp(q, t_v2, r)
    assert r.status_code == 200
    assert isinstance(response, PlainTextResponse)
    content = literal_eval(response.body.decode("utf-8"))
    expected2: Dict[str, Dict[str, List[Any]]] = {
        "results": {
            "bindings": [
                {
                    "pred": {
                        "type": "uri",
                        "value": "https://www.w3schools.com/rdf/bar",
                    },
                    "obj": {"type": "literal", "value": "bbbbbbbbbbbbbbb"},
                },
                {
                    "pred": {
                        "type": "uri",
                        "value": "https://www.w3schools.com/rdf/bar",
                    },
                    "obj": {"type": "literal", "value": "007"},
                },
                {
                    "pred": {
                        "type": "uri",
                        "value": "https://www.w3schools.com/rdf/foo",
                    },
                    "obj": {"type": "literal", "value": "aaaaaaaaaaaaaaaaaaaaaaaaa"},
                },
                {
                    "pred": {
                        "type": "uri",
                        "value": "https://www.w3schools.com/rdf/foo",
                    },
                    "obj": {"type": "literal", "value": "00"},
                },
            ]
        },
        "head": {"vars": ["pred", "obj"]},
    }

    assert sorted(content["head"]["vars"]) == sorted(expected2["head"]["vars"])
    assert sorted(
        content["results"]["bindings"], key=lambda a: a["obj"]["value"]
    ) == sorted(expected2["results"]["bindings"], key=lambda a: a["obj"]["value"])

    # Query with timestamp t_v1 should yeld union of A and v1 of B
    r = Response()
    response = get_api_sparql_timestamp(q, t_v1, r)
    assert r.status_code == 200
    assert isinstance(response, PlainTextResponse)
    content = literal_eval(response.body.decode("utf-8"))
    expected3: Dict[str, Dict[str, List[Any]]] = {
        "results": {
            "bindings": [
                {
                    "pred": {
                        "type": "uri",
                        "value": "https://www.w3schools.com/rdf/bar",
                    },
                    "obj": {"type": "literal", "value": "baz"},
                },
                {
                    "pred": {
                        "type": "uri",
                        "value": "https://www.w3schools.com/rdf/bar",
                    },
                    "obj": {"type": "literal", "value": "007"},
                },
                {
                    "pred": {
                        "type": "uri",
                        "value": "https://www.w3schools.com/rdf/foo",
                    },
                    "obj": {"type": "literal", "value": "Bar"},
                },
                {
                    "pred": {
                        "type": "uri",
                        "value": "https://www.w3schools.com/rdf/foo",
                    },
                    "obj": {"type": "literal", "value": "00"},
                },
            ]
        },
        "head": {"vars": ["pred", "obj"]},
    }

    assert sorted(content["head"]["vars"]) == sorted(expected3["head"]["vars"])
    assert sorted(
        content["results"]["bindings"], key=lambda a: a["obj"]["value"]
    ) == sorted(expected3["results"]["bindings"], key=lambda a: a["obj"]["value"])
