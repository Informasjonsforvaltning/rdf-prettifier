"""Contract tests."""

from ast import literal_eval
from math import ceil
from textwrap import dedent
import time
from urllib.parse import quote

import pytest

requests = pytest.importorskip("requests")


@pytest.mark.contract
def test_readyz(service: str) -> None:
    """Test readiness."""
    response = requests.get(f"{service}/readyz")
    assert response.status_code == 200


@pytest.mark.contract
def test_livez(service: str) -> None:
    """Test liveness."""
    response = requests.get(f"{service}/livez")
    assert response.status_code == 200


@pytest.mark.contract
def test_store_graph_forbidden_when_missing_api_key(service: str) -> None:
    """Test graph storage forbidden."""
    data = {
        "id": "<http://foo/bar¡@½@$}135[¥}¡35>",
        "graph": """
        @prefix si: <https://www.w3schools.com/rdf/> .

        <https://digdir.no/dataset/007> si:author "James Bond" ;
            si:title "The man!" .
        """,
    }
    response = requests.post(f"{service}/api/graphs", json=data)
    assert response.status_code == 403


@pytest.mark.contract
def test_store_graph(service: str) -> None:
    """Test graph storage."""
    data = {
        "id": "<http://foo/bar¡@½@$}135[¥}¡35>",
        "graph": """
        @prefix si: <https://www.w3schools.com/rdf/> .

        <https://digdir.no/dataset/007> si:author "James Bond" ;
            si:title "The man!" .
        """,
    }
    response = requests.post(
        f"{service}/api/graphs", headers={"X-API-KEY": "test-key"}, json=data
    )
    assert response.status_code == 200


@pytest.mark.contract
def test_get_metadata(service: str) -> None:
    """Test graph metdata."""
    response = requests.get(
        f"{service}/api/metadata",
        headers={"X-API-KEY": "test-key"},
    )
    assert response.status_code == 200
    # literal_eval does not fancy 'false' in json, but rather 'False'
    content = literal_eval(response.content.decode("utf-8").replace("false", "False"))
    assert not content["empty"]
    assert 1665409969 < content["start_time"] < 2065409969


@pytest.mark.contract
def test_load_graph(service: str) -> None:
    """Test graph retrieval."""
    graph_id = "<http://foo/bar¡@½@$}135[¥}¡35>"
    expected = """
        @prefix si: <https://www.w3schools.com/rdf/> .

        <https://digdir.no/dataset/007> si:author "James Bond" ;
            si:title "The man!" .
        """
    response = requests.get(f"{service}/api/graphs?id={quote(graph_id)}")
    assert response.content.decode("utf-8") == dedent(expected).strip()


@pytest.mark.contract
def test_sparql_query(service: str) -> None:
    """Test sparql query."""
    q = (
        "PREFIX%20si%3A%20%3Chttps%3A%2F%2Fwww.w3schools.com%2Frdf%2F%3E%0ASELECT%20*%20"
        + "WHERE%20%7B%0A%20%20%3Chttps%3A%2F%2Fdigdir.no%2Fdataset%2F007%3E%20si%3Aauthor%20%3Fobj%20.%0A%7D%20"
        + "LIMIT%2010"
    )
    response = requests.get(f"{service}/api/sparql?query={q}")
    content = literal_eval(response.content.decode("utf-8"))
    assert content["results"]["bindings"] == [
        {"obj": {"type": "literal", "value": "James Bond"}}
    ]
    assert content["head"]["vars"] == ["obj"]


@pytest.mark.contract
def test_sparql_query_timestamp(service: str) -> None:
    """Test sparql query with specific timestamp."""
    q = (
        "PREFIX%20si%3A%20%3Chttps%3A%2F%2Fwww.w3schools.com%2Frdf%2F%3E%0ASELECT%20*%20"
        + "WHERE%20%7B%0A%20%20%3Chttps%3A%2F%2Fdigdir.no%2Fdataset%2F007%3E%20si%3Aauthor%20%3Fobj%20.%0A%7D%20"
        + "LIMIT%2010"
    )
    response = requests.get(f"{service}/api/sparql/{ceil(time.time())}?query={q}")
    raw_content = response.content.decode("utf-8")
    content = literal_eval(raw_content)
    assert content["results"]["bindings"] == [
        {"obj": {"type": "literal", "value": "James Bond"}}
    ]
    assert content["head"]["vars"] == ["obj"]


@pytest.mark.contract
def test_delete_graph_forbidden_when_missing_api_key(service: str) -> None:
    """Test graph deletion."""
    response = requests.delete(f"{service}/api/graphs?id=rm-rf")
    assert response.status_code == 403


@pytest.mark.contract
def test_delete_graph(service: str) -> None:
    """Test graph deletion."""
    data = {
        "id": "rm-rf",
        "graph": """
        @prefix si: <https://www.w3schools.com/rdf/> .

        <https://digdir.no/dataset/007> si:author "James Bond" ;
            si:title "The man!" .
        """,
    }
    response = requests.post(
        f"{service}/api/graphs", headers={"X-API-KEY": "test-key"}, json=data
    )

    graph_id = quote("rm-rf")
    response = requests.delete(
        f"{service}/api/graphs?id={graph_id}", headers={"X-API-KEY": "test-key"}
    )
    assert response.status_code == 200
    response = requests.get(f"{service}/api/graphs?id={graph_id}")
    assert response.status_code == 404
    assert response.content.decode("utf-8") == '{"message":"No such graph: \'rm-rf\'"}'


@pytest.mark.contract
def test_get_at_timestamp(service: str) -> None:
    """Get graph at specific time."""
    graphs = []
    graph_id = "d4t3t1m3"

    for i in range(3):
        data = {
            "id": graph_id,
            "graph": f"""
            @prefix si: <https://www.w3schools.com/rdf/> .

            <https://www.w3schools.com> si:author "Jan Egil Refsnes" ;
                si:title "W3Schools{i}" .
            """,
        }
        response = requests.post(
            f"{service}/api/graphs", headers={"X-API-KEY": "test-key"}, json=data
        )
        assert response.status_code == 200

        graphs.append((data, int(time.time())))
        time.sleep(2)

    response = requests.delete(
        f"{service}/api/graphs?id={graph_id}", headers={"X-API-KEY": "test-key"}
    )
    assert response.status_code == 200
    response = requests.get(f"{service}/api/graphs?id={graph_id}")
    assert response.status_code == 404

    for _i, (graph, t) in enumerate([*graphs, *graphs[::-1]]):
        response = requests.get(f"{service}/api/graphs/{t}?id={graph_id}")
        assert response.status_code == 200
        assert response.content.decode("utf-8") == dedent(graph["graph"]).strip()

    response = requests.get(f"{service}/api/graphs/{int(time.time())}?id={graph_id}")
    assert response.status_code == 404
    assert (
        response.content.decode("utf-8")
        == f'{{"message":"No such graph: \'{graph_id}\'"}}'
    )
