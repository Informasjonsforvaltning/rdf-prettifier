import asyncio

import logging
import time

from typing import Optional, Union

from fastapi import Depends, FastAPI, Request, Response
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.security.api_key import APIKey

from .auth import get_api_key
from .git import (
    delete_graph,
    load_graph,
    repo_metadata,
    store_graph,
)
from .models import Graph, HTTPError, Message, Metadata
from .rdf import load_all_graphs, load_all_graphs_raw, to_turtle
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


@app.middleware("http")
async def timeout_middleware(request: Request, call_next):
    """Timeout middleware."""
    try:
        start_time = time.time()
        return await asyncio.wait_for(call_next(request), timeout=5)

    except asyncio.TimeoutError:
        process_time = time.time() - start_time
        return JSONResponse({"error":
            f"Request processing time excedeed limit: {process_time}",
        }, status_code=500)


@app.get(
    "/api/graphs",
    response_model=Union[str, Message, HTTPError],
    responses={"404": {"model": Message}, "500": {"model": HTTPError}},
)
async def get_api_graphs(
    response: Response,
    id: Optional[str] = None,
    raw: Optional[str] = None,
) -> Union[PlainTextResponse, Message, HTTPError]:
    """
    Get current graph(s).
    """
    try:
        if id:
            try:
                return PlainTextResponse(await load_graph(id, None))
            except FileNotFoundError:
                response.status_code = 404
                return Message(message=f"No such graph: '{id}'")
        else:
            if isinstance(raw, str) and raw == "true":
                return PlainTextResponse(await load_all_graphs_raw(None))
            else:
                return PlainTextResponse(await load_all_graphs(None))
    except Exception as e:
        response.status_code = 500
        return HTTPError(error=str(e))


@app.get(
    "/api/graphs/{timestamp}",
    response_model=Union[str, Message, HTTPError],
    responses={"404": {"model": Message}, "500": {"model": HTTPError}},
)
async def get_api_graphs_timestamp(
    response: Response,
    timestamp: int,
    id: Optional[str] = None,
    raw: Optional[str] = None,
) -> Union[PlainTextResponse, Message, HTTPError]:
    """Get graph(s) at specific time."""
    try:
        if id:
            try:
                return PlainTextResponse(await load_graph(id, timestamp))
            except FileNotFoundError:
                response.status_code = 404
                return Message(message=f"No such graph: '{id}'")
        else:
            if isinstance(raw, str) and raw == "true":
                return PlainTextResponse(await load_all_graphs_raw(timestamp))
            else:
                return PlainTextResponse(await load_all_graphs(timestamp))
    except Exception as e:
        response.status_code = 500
        return HTTPError(error=str(e))


@app.get(
    "/api/sparql",
    response_model=Union[str, HTTPError],
    responses={"500": {"model": HTTPError}},
)
async def get_api_sparql(
    response: Response, query: str
) -> Union[PlainTextResponse, HTTPError]:
    """Query current graphs with SparQL."""
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
    response: Response, timestamp: int, query: str
) -> Union[PlainTextResponse, HTTPError]:
    """Query specific timestamp with SparQL."""
    try:
        return PlainTextResponse(await query_sparql(query, timestamp))
    except Exception as e:
        response.status_code = 500
        return HTTPError(error=str(e))


@app.post("/api/graphs", response_model=None, responses={"500": {"model": HTTPError}})
async def post_api_graphs(
    response: Response, body: Graph, api_key: APIKey = Depends(get_api_key)
) -> Union[None, HTTPError]:
    """Store graph."""
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
    response: Response, id: str, api_key: APIKey = Depends(get_api_key)
) -> Union[None, Message, HTTPError]:
    """Delete graph."""
    try:
        await delete_graph(id)
        return None
    except FileNotFoundError:
        response.status_code = 404
        return Message(message=f"No such graph: '{id}'")
    except Exception as e:
        response.status_code = 500
        return HTTPError(error=str(e))


@app.get(
    "/api/metadata",
    response_model=Union[Metadata, HTTPError],
    responses={"500": {"model": HTTPError}},
)
async def get_api_metadata(response: Response) -> Union[Metadata, HTTPError]:
    """Get diff-store metadata."""
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
