"""Command-line entry point (`advance-rag ...`). Later phases add `reindex`, `eval`, etc."""

# pyrefly: ignore [missing-import]
import typer
import uvicorn

from advance_rag import __version__

app = typer.Typer(name="advance-rag", no_args_is_help=True, help="Advance RAG platform CLI.")


@app.command()
def serve(host: str = "127.0.0.1", port: int = 8000, reload: bool = False) -> None:
    """Run the API server."""
    uvicorn.run(
        "advance_rag.api.app:create_app",
        factory=True,
        host=host,
        port=port,
        reload=reload,
        access_log=False,  # RequestContextMiddleware emits structured access logs
    )


@app.command()
def version() -> None:
    """Print the installed version."""
    typer.echo(__version__)
