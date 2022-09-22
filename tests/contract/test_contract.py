"""Contract tests."""

from textwrap import dedent

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
    response = requests.post(f"{service}/api/graphs", json=data)
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
    response = requests.post(f"{service}/api/graphs", json=data)

    data = {
        "id": "rm-rf",
    }
    response = requests.delete(f"{service}/api/graphs", json=data)
    assert response.status_code == 200

    response = requests.get(f"{service}/api/graphs", json=data)
    assert response.status_code == 404
    assert response.content.decode("utf-8") == '{"message":"No such graph: \'rm-rf\'"}'
