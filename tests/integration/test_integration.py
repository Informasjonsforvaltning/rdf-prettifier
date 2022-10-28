"""Integration tests."""

from textwrap import dedent

from fastapi import Response
import pytest

from rdf_prettifier.main import prettify_graph
from rdf_prettifier.models import Graph


@pytest.mark.integration
def test_pretty_print_turtle() -> None:
    """Test conversion.

    Assert successful conversion and pretty print of RDF graph.
    """
    input_graph = """
        @prefix si: <https://www.w3schools.com/rdf/> .

        <https://www.w3schools00.com> si:author "Jan Egil Refsnes" ;
            si:title "W3Schools" ;
            si:randomentry "W3Schools" .

        <https://www.w3schools01.com> si:author "Jan Egil Refsnes" .
        <https://www.w3schools01.com> si:title "W3Schools" .

        <https://www.w3schools02.com> si:author "John Doe" ;
            si:title "W3Schools" .
    """
    body = Graph(
        graph=input_graph, input_format="text/turtle", output_format="text/turtle"
    )
    expected_graph = """
        @prefix si: <https://www.w3schools.com/rdf/> .

        <https://www.w3schools00.com> si:author "Jan Egil Refsnes" ;
            si:randomentry "W3Schools" ;
            si:title "W3Schools" .

        <https://www.w3schools01.com> si:author "Jan Egil Refsnes" ;
            si:title "W3Schools" .

        <https://www.w3schools02.com> si:author "John Doe" ;
            si:title "W3Schools" .
    """

    r = Response()
    response = prettify_graph(r, body)
    assert r.status_code == 200
    assert isinstance(response, Response)
    assert response.body.decode("utf-8") == dedent(expected_graph).strip()


@pytest.mark.integration
def test_pretty_print_malformed_turtle() -> None:
    """Test conversion.

    Assert HTTPError from pretty print with invalid graph.
    """
    input_graph = """
        @prefix si: <https://www.w3schools.com/rdf/> .

        https://www.w3schools00.com> si:author "Jan Egil Refsnes" ;
            si:title "W3Schools" .
            si:randomentry "W3Schools" .

        <https://www.w3schools01.com> si:author "Jan Egil Refsnes" .
        <https://www.w3schools01.com> si:title "W3Schools" .

        <https://www.w3schools02.com> si:author "John Doe" .
            si:title "W3Schools" ;
    """

    body = Graph(
        graph=input_graph, input_format="text/turtle", output_format="text/turtle"
    )
    r = Response()
    prettify_graph(r, body)

    assert r.status_code == 500
