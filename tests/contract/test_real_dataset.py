import pytest

requests = pytest.importorskip("requests")

DATASET = """
@prefix adms:     <http://www.w3.org/ns/adms#> .
@prefix dc:       <http://purl.org/dc/elements/1.1/> .
@prefix dcat:     <http://www.w3.org/ns/dcat#> .
@prefix dct:      <http://purl.org/dc/terms/> .
@prefix dcterms:  <http://purl.org/dc/terms/> .
@prefix dctype:   <http://purl.org/dc/dcmitype/> .
@prefix foaf:     <http://xmlns.com/foaf/0.1/> .
@prefix gco:      <http://www.isotc211.org/2005/gco> .
@prefix gmd:      <http://www.isotc211.org/2005/gmd> .
@prefix gml:      <http://www.opengis.net/gml> .
@prefix locn:     <http://www.w3.org/ns/locn#> .
@prefix owl:      <http://www.w3.org/2002/07/owl#> .
@prefix rdf:      <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs:     <http://www.w3.org/2000/01/rdf-schema#> .
@prefix skos:     <http://www.w3.org/2004/02/skos/core#> .
@prefix vcard:    <http://www.w3.org/2006/vcard/ns#> .
@prefix void:     <http://www.w3.org/TR/void/> .
@prefix xslUtils: <java:org.fao.geonet.util.XslUtil> .

<https://kartkatalog.geonorge.no/Metadata/uuid/1480a012-ba90-43c1-92bd-cc6977b5e7cf>
        rdf:type                    dcat:Dataset ;
        dcterms:accessRights        <http://publications.europa.eu/resource/authority/access-right/PUBLIC> ;
        dcterms:accrualPeriodicity  "continual" ;
        dcterms:description         "Temasettet viser nasjonale laksefjorder i Finnmark, avgrenset etter N50."@no ;
        dcterms:identifier          "1480a012-ba90-43c1-92bd-cc6977b5e7cf" ;
        dcterms:license             <http://inspire.ec.europa.eu/metadata-codelist/ConditionsApplyingToAccessAndUse/noConditionsApply> ;
        dcterms:publisher           "" ;
        dcterms:spatial             <https://kartkatalog.geonorge.no/Metadata/uuid/1480a012-ba90-43c1-92bd-cc6977b5e7cf/.well-known/skolem/d397fc6d-1cf8-48a3-bfb0-39b86e7b096a> ;
        dcterms:title               "Nasjonale laksefjorder i Finnmark"@no ;
        dcterms:updated             ""^^<http://www.w3.org/2001/XMLSchema#date> ;
        dcat:contactPoint           "" ;
        dcat:dataQuality            "Ingen prosseshistorie tilgjenglig." ;
        dcat:distribution           <https://kartkatalog.geonorge.no/Metadata/uuid/1480a012-ba90-43c1-92bd-cc6977b5e7cf/AI> ;
        dcat:granularity            "50000" ;
        dcat:keyword                "Finnmark"@no , "fellesDatakatalog"@no , "Kyst og fiskeri"@no , "Finnmark fylke"@no , "villaks"@no , "Nasjonale"@no , "modellbaserteVegprosjekter"@no , "Norge digitalt"@no , "laksefjord"@no , "laks"@no , "fylke"@no , "Annet"@no ;
        dcat:theme                  <http://publications.europa.eu/resource/authority/data-theme/AGRI> , <https://register.geonorge.no/subregister/metadata-kodelister/kartverket/nasjonal-temainndeling/kartverket/kyst-og-fiskeri> ;
        foaf:thumbnail              <http://www.geonorge.no/thumbnails_sk/Nasjonale_laksefjorder.png> .

<http://publications.europa.eu/resource/authority/data-theme/AGRI>
        rdf:type        skos:Concept ;
        skos:inScheme   <http://publications.europa.eu/mdr/resource/authority/data-theme/html/data-theme-eng.html> ;
        skos:prefLabel  "Agriculture, fisheries, forestry and food"@en .

<http://publications.europa.eu/mdr/resource/authority/data-theme/html/data-theme-eng.html>
        rdf:type       skos:ConceptScheme ;
        dcterms:title  "MDR data themes"@en .

<https://register.geonorge.no/subregister/metadata-kodelister/kartverket/nasjonal-temainndeling/kartverket/kyst-og-fiskeri>
        rdf:type        skos:Concept ;
        skos:inScheme   <https://register.geonorge.no/subregister/metadata-kodelister/kartverket/nasjonal-temainndeling> ;
        skos:prefLabel  "Kyst og fiskeri"@no .

<https://kartkatalog.geonorge.no/Metadata/uuid/1480a012-ba90-43c1-92bd-cc6977b5e7cf/.well-known/skolem/d397fc6d-1cf8-48a3-bfb0-39b86e7b096a>
        locn:geometry  "<gml:Envelope srsName=\\"http://www.opengis.net/def/crs/OGC/1.3/CRS84\\"><gml:lowerCorner>20,2371979624437 68,1542746119889</gml:lowerCorner><gml:upperCorner>31,9388137578975 71,4715028441541</gml:upperCorner></gml:Envelope>"^^<http://www.opengis.net/ont/geosparql#gmlLiteral> .

<https://kartkatalog.geonorge.no/Metadata/uuid/1480a012-ba90-43c1-92bd-cc6977b5e7cf/AI>
        rdf:type             dcat:Distribution ;
        dcterms:description  "Webside eller webløsning hvor en etat tibyr nedlastning av data direkte eller gjennom ulike grafiske brukergrensesnitt" ;
        dcterms:format       "AI" ;
        dcterms:license      <http://inspire.ec.europa.eu/metadata-codelist/ConditionsApplyingToAccessAndUse/noConditionsApply> ;
        dcterms:title        "Egen nedlastningsside"@no ;
        adms:status          "" ;
        dcat:accessURL       <https://kartkatalog.geonorge.no/metadata/uuid/1480a012-ba90-43c1-92bd-cc6977b5e7cf> .

<https://register.geonorge.no/subregister/metadata-kodelister/kartverket/nasjonal-temainndeling>
        rdf:type       skos:ConceptScheme ;
        dcterms:title  "Nasjonal temainndeling for geografiske data"@no .
"""


@pytest.mark.contract
def test_store_real_graph(service: str) -> None:
    """Test graph storage."""
    data = {
        "id": "1480a012-ba90-43c1-92bd-cc6977b5e7cf",
        "graph": DATASET.replace("\n", ""),
        "format": "text/turtle",
    }
    response = requests.post(
        f"{service}/api/graphs", headers={"X-API-KEY": "test-key"}, json=data
    )
    print(response.content.decode("utf-8"))
    assert response.status_code == 200
