"""Advance RAG — multi-tenant enterprise knowledge infrastructure with RAG as its intelligence layer."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("advance-rag")
except PackageNotFoundError:  # pragma: no cover - only when running from a raw checkout
    __version__ = "0.0.0"
