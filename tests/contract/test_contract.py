"""Contract tests."""

from textwrap import dedent
import time

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
def test_load_graph(service: str) -> None:
    """Test graph retrieval."""
    data = {"id": "<http://foo/bar¡@½@$}135[¥}¡35>"}
    expected = """
        @prefix si: <https://www.w3schools.com/rdf/> .

        <https://digdir.no/dataset/007> si:author "James Bond" ;
            si:title "The man!" .
        """
    response = requests.get(f"{service}/api/graphs", json=data)
    assert response.content.decode("utf-8") == dedent(expected).strip()


@pytest.mark.contract
def test_delete_graph_forbidden_when_missing_api_key(service: str) -> None:
    """Test graph deletion."""
    id = {
        "id": "rm-rf",
    }
    response = requests.delete(f"{service}/api/graphs", json=id)
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

    id = {
        "id": "rm-rf",
    }
    response = requests.delete(
        f"{service}/api/graphs", headers={"X-API-KEY": "test-key"}, json=id
    )
    assert response.status_code == 200
    response = requests.get(f"{service}/api/graphs", json=id)
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

        graphs.append((data, time.time()))
        time.sleep(2)

    id = {
        "id": graph_id,
    }
    response = requests.delete(
        f"{service}/api/graphs", headers={"X-API-KEY": "test-key"}, json=id
    )
    assert response.status_code == 200
    response = requests.get(f"{service}/api/graphs", json=id)
    assert response.status_code == 404

    for _i, (graph, t) in enumerate([*graphs, *graphs[::-1]]):
        tid = {
            "id": graph_id,
            "timestamp": t,
        }
        response = requests.get(f"{service}/api/graphs", json=tid)
        assert response.status_code == 200
        assert response.content.decode("utf-8") == dedent(graph["graph"]).strip()

    tid = {
        "id": graph_id,
        "timestamp": time.time(),
    }
    response = requests.get(f"{service}/api/graphs", json=tid)
    assert response.status_code == 404
    assert (
        response.content.decode("utf-8")
        == f'{{"message":"No such graph: \'{graph_id}\'"}}'
    )
