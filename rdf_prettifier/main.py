"""This module provides an API to prettify a given RDF graph."""

from typing import Union

from fastapi import Depends, FastAPI, Response
from fastapi.security.api_key import APIKey

from .auth import get_api_key
from .models import Graph, HTTPError
from .rdf import prettify

app = FastAPI(
    title="rdf-prettifier",
    description="Prettifies an RDF graph",
    version="0.1.0",
)

API_KEY: APIKey = Depends(get_api_key)


@app.post("/api/prettify", response_model=None, responses={"500": {"model": HTTPError}})
def prettify_graph(
    response: Response, body: Graph, api_key: APIKey = API_KEY
) -> Union[Response, HTTPError]:
    """Return pretty printed graph."""
    try:
        prettified = prettify(body.graph, body.input_format, body.output_format)
        return Response(content=prettified, media_type=body.output_format)
    except Exception as e:
        response.status_code = 500
        return HTTPError(error=str(e))


@app.get("/livez")
def get_livez() -> str:
    """Endpoint for liveness probe."""
    return "ok"


@app.get("/readyz")
def get_readyz() -> str:
    """Endpoint for readiness probe."""
    return "ok"
