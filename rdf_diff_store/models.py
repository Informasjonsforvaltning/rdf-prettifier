from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class HTTPError(BaseModel):
    message: Optional[str] = None
    error: Optional[str] = None


class Message(BaseModel):
    message: Optional[str] = None


class Metadata(BaseModel):
    empty: bool
    start_time: Optional[int] = Field(None, description="Seconds since epoch")


class Graph(BaseModel):
    id: str
    format: Optional[str] = None
    graph: str
