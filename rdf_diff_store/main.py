from __future__ import annotations

from typing import Union

from fastapi import FastAPI, Response
from fastapi.responses import PlainTextResponse

from .git import delete_graph, load_graph, store_graph
from .models import Graph, HTTPError, ID, Message, TemporalID
from .rdf import to_turtle

app = FastAPI(
    title="rdf-diff-store",
    description="Historical storage for rdf",
    version="0.1.0",
)


@app.get(
    "/api/graphs",
    response_model=Union[str, Message, HTTPError],
    responses={"404": {"model": Message}, "500": {"model": HTTPError}},
)
def get_api_graphs(
    body: TemporalID, response: Response
) -> Union[PlainTextResponse, Message, HTTPError]:
    """
    Get graph at specific time
    """
    try:
        return PlainTextResponse(load_graph(body.id))
    except FileNotFoundError:
        response.status_code = 404
        return Message(message=f"No such graph: '{body.id}'")
    except Exception as e:
        response.status_code = 500
        return HTTPError(error=str(e))


@app.post("/api/graphs", response_model=None, responses={"500": {"model": HTTPError}})
def post_api_graphs(body: Graph) -> Union[None, HTTPError]:
    """
    Store graph
    """
    try:
        turtle = to_turtle(body.graph, body.format)
        store_graph(body.id, turtle)
        return None
    except Exception as e:
        return HTTPError(error=str(e))


@app.delete("/api/graphs", response_model=None, responses={"500": {"model": HTTPError}})
def delete_api_graphs(body: ID) -> Union[None, HTTPError]:
    """
    Delete graph
    """
    try:
        delete_graph(body.id)
        return None
    except Exception as e:
        return HTTPError(error=str(e))


@app.get("/livez")
def get_livez() -> str:
    """Endpoint for liveness probe."""
    return "ok"


@app.get("/readyz")
def get_readyz() -> str:
    """Endpoint for readiness probe."""
    return "ok"
