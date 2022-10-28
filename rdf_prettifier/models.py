"""This module provides models for RDF prettifier."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class HTTPError(BaseModel):
    """HTTPError."""

    message: Optional[str] = None
    error: Optional[str] = None


class Graph(BaseModel):
    """Graph Class."""

    input_format: Optional[str] = None
    graph: str
    output_format: Optional[str] = "turtle"
