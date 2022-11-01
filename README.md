# rdf-diff-store

API for versioning RDF and retrieving RDF graphs at any point in time

## Development

Setup:

```bash
poetry install
```

Run locally:

```bash
poetry run uvicorn rdf_diff_store.main:app --reload
```

Generate code (after updating openapi spec):

```bash
nox -s openapi
```
