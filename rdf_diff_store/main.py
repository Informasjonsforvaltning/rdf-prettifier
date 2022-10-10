from __future__ import annotations

import logging

from typing import Optional, Union

from fastapi import Depends, FastAPI, Response
from fastapi.responses import PlainTextResponse
from fastapi.security.api_key import APIKey

from .auth import get_api_key
from .git import delete_graph, load_graph, repo_metadata, store_graph
from .models import Graph, HTTPError, ID, Message, Metadata, TemporalID
from .rdf import to_turtle
from .sparql import query_sparql

app = FastAPI(
    title="rdf-diff-store",
    description="Historical storage for rdf",
    version="0.1.0",
)


# Dont log /livez and /readyz
class EndpointFilter(logging.Filter):
    """Filter."""

    def filter(self, record: logging.LogRecord) -> bool:
        """Filter."""
        return (
            record.getMessage().find("/livez") == -1
            and record.getMessage().find("/readyz") == -1
        )


logging.getLogger("uvicorn.access").addFilter(EndpointFilter())


@app.get(
    "/api/graphs",
    response_model=Union[str, Message, HTTPError],
    responses={"404": {"model": Message}, "500": {"model": HTTPError}},
)
async def get_api_graphs(
    body: TemporalID, response: Response
) -> Union[PlainTextResponse, Message, HTTPError]:
    """
    Get graph at specific time
    """
    try:
        return PlainTextResponse(await load_graph(body.id, body.timestamp))
    except FileNotFoundError:
        response.status_code = 404
        return Message(message=f"No such graph: '{body.id}'")
    except Exception as e:
        response.status_code = 500
        return HTTPError(error=str(e))


@app.get(
    "/api/sparql",
    response_model=Union[str, HTTPError],
    responses={"500": {"model": HTTPError}},
)
async def get_api_sparql(
    query: str, response: Response
) -> Union[PlainTextResponse, HTTPError]:
    """
    Query current time with SparQL
    """
    try:
        return PlainTextResponse(await query_sparql(query, None))
    except Exception as e:
        response.status_code = 500
        return HTTPError(error=str(e))


@app.get(
    "/api/sparql/{timestamp}",
    response_model=Union[str, HTTPError],
    responses={"500": {"model": HTTPError}},
)
async def get_api_sparql_timestamp(
    query: str, timestamp: Optional[int], response: Response
) -> Union[PlainTextResponse, HTTPError]:
    """
    Query specific timestamp with SparQL
    """
    try:
        return PlainTextResponse(await query_sparql(query, timestamp))
    except Exception as e:
        response.status_code = 500
        return HTTPError(error=str(e))


@app.post("/api/graphs", response_model=None, responses={"500": {"model": HTTPError}})
async def post_api_graphs(
    body: Graph, response: Response, api_key: APIKey = Depends(get_api_key)
) -> Union[None, HTTPError]:
    """
    Store graph
    """
    try:
        turtle = to_turtle(body.graph, body.format)
        await store_graph(body.id, turtle)
        return None
    except Exception as e:
        response.status_code = 500
        return HTTPError(error=str(e))


@app.delete(
    "/api/graphs",
    response_model=Union[None, Message, HTTPError],
    responses={"404": {"model": Message}, "500": {"model": HTTPError}},
)
async def delete_api_graphs(
    body: ID, response: Response, api_key: APIKey = Depends(get_api_key)
) -> Union[None, Message, HTTPError]:
    """
    Delete graph
    """
    try:
        await delete_graph(body.id)
        return None
    except FileNotFoundError:
        response.status_code = 404
        return Message(message=f"No such graph: '{body.id}'")
    except Exception as e:
        response.status_code = 500
        return HTTPError(error=str(e))


@app.get(
    "/api/metadata",
    response_model=Union[Metadata, HTTPError],
    responses={"500": {"model": HTTPError}},
)
async def get_api_metadata(response: Response) -> Union[Metadata, HTTPError]:
    """
    Get diff-store metadata.
    """
    try:
        return await repo_metadata()
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
