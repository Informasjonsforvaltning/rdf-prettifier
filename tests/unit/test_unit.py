"""Unit tests."""

from textwrap import dedent

import pytest

from rdf_diff_store.rdf import to_turtle


@pytest.mark.unit
def test_parse_xml() -> None:
    """Test xml."""
    xml = """
        <?xml version="1.0"?>

        <rdf:RDF
        xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
        xmlns:si="https://www.w3schools.com/rdf/">

        <rdf:Description rdf:about="https://www.w3schools.com">
        <si:title>W3Schools</si:title>
        <si:author>Jan Egil Refsnes</si:author>
        </rdf:Description>

        </rdf:RDF>
        """
    turtle = """
        @prefix si: <https://www.w3schools.com/rdf/> .

        <https://www.w3schools.com> si:author "Jan Egil Refsnes" ;
            si:title "W3Schools" .
        """

    assert to_turtle(graph=xml, format="application/rdf+xml") == dedent(turtle).strip()
