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
def test_request_forbidden_when_missing_api_key(service: str) -> None:
    """Test forbidden request when missing api key."""
    data = {
        "input_format": "text/turtle",
        "output_format": "text/turtle",
        "graph": """
        @prefix si: <https://www.w3schools.com/rdf/> .

        <https://digdir.no/dataset/007> si:author "James Bond" ;
            si:title "The man!" .
        """,
    }
    response = requests.post(f"{service}/api/prettify", json=data)
    assert response.status_code == 403


@pytest.mark.contract
def test_successful_response_valid_turtle(service: str) -> None:
    """Test successful response with valid turtle."""
    data = {
        "input_format": "text/turtle",
        "output_format": "text/turtle",
        "graph": """
        @prefix si: <https://www.w3schools.com/rdf/> .

        <https://www.w3schools00.com> si:author "Jan Egil Refsnes" ;
            si:title "W3Schools" ;
            si:randomentry "W3Schools" .

        <https://www.w3schools01.com> si:author "Jan Egil Refsnes" .
        <https://www.w3schools01.com> si:title "W3Schools" .

        <https://www.w3schools02.com> si:author "John Doe" ;
            si:title "W3Schools" .
    """,
    }
    expected = """
        @prefix si: <https://www.w3schools.com/rdf/> .

        <https://www.w3schools00.com> si:author "Jan Egil Refsnes" ;
            si:randomentry "W3Schools" ;
            si:title "W3Schools" .

        <https://www.w3schools01.com> si:author "Jan Egil Refsnes" ;
            si:title "W3Schools" .

        <https://www.w3schools02.com> si:author "John Doe" ;
            si:title "W3Schools" .
    """
    response = requests.post(
        f"{service}/api/prettify", headers={"X-API-KEY": "test-key"}, json=data
    )
    assert response.status_code == 200
    assert response.content.decode("utf-8") == dedent(expected).strip()


@pytest.mark.contract
def test_response_invalid_turtle(service: str) -> None:
    """Test successful response with valid turtle."""
    data = {
        "input_format": "text/turtle",
        "output_format": "text/turtle",
        "graph": """
        @prefix si: <https://www.w3schools.com/rdf/> .

        https://www.w3schools00.com> si:author "Jan Egil Refsnes" ;
            si:title "W3Schools" .
            si:randomentry "W3Schools" .

        <https://www.w3schools01.com> si:author "Jan Egil Refsnes" .
        <https://www.w3schools01.com> si:title "W3Schools" .

        <https://www.w3schools02.com> si:author "John Doe" .
            si:title "W3Schools" ;
        """,
    }
    response = requests.post(
        f"{service}/api/prettify", headers={"X-API-KEY": "test-key"}, json=data
    )
    assert response.status_code == 500


@pytest.mark.contract
def test_response_invalid_format_definition(service: str) -> None:
    """Test successful response with valid turtle."""
    data = {
        "input_format": "text/turtle",
        "output_format": "invald_format_specification",
        "graph": """
        @prefix si: <https://www.w3schools.com/rdf/> .

        <https://www.w3schools00.com> si:author "Jan Egil Refsnes" ;
            si:randomentry "W3Schools" .
            si:title "W3Schools" ;

        <https://www.w3schools01.com> si:author "Jan Egil Refsnes" .
        """,
    }
    response = requests.post(
        f"{service}/api/prettify", headers={"X-API-KEY": "test-key"}, json=data
    )
    assert response.status_code == 500
