# rdf-prettifier

API returning prettified version of RDF.
(Supported input and output formats)[https://rdflib.readthedocs.io/en/stable/plugin_serializers.html].

## Development

Setup:

```bash
poetry install
```

Run locally:

```bash
poetry run uvicorn rdf_prettifier.main:app --reload
```

Generate code (after updating openapi spec):

```bash
nox -s openapi
```
