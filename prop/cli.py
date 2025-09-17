"""Typer-based CLI wrapper (Prompt 10).

Commands:
  prop intake FILES...    -> Calls local /api/bid/intake-parse and prints Opportunity JSON.
  prop score --json PATH  -> Calls local /api/bid/score with opportunity JSON and prints Decision Card.
"""

from __future__ import annotations

import json
from pathlib import Path
import typer
import requests

APP = typer.Typer(add_completion=False, help="Proposal Bot CLI")

DEFAULT_BASE = "http://127.0.0.1:8000"


def _base_url() -> str:
    return DEFAULT_BASE.rstrip("/")


@APP.command()
def intake(
    files: list[Path] = typer.Argument(..., exists=True, readable=True, resolve_path=True),
    base: str = typer.Option(DEFAULT_BASE, help="Base URL for API"),
):
    """Parse input requirement docs into an Opportunity skeleton."""
    payload = {"files": [str(f) for f in files]}
    url = f"{base.rstrip('/')}/api/bid/intake-parse"
    try:
        r = requests.post(url, json=payload, timeout=60)
    except Exception as e:
        typer.echo(f"[error] request failed: {e}", err=True)
        raise typer.Exit(code=2)
    if not r.ok:
        typer.echo(f"[error] {r.status_code} {r.text}", err=True)
        raise typer.Exit(code=1)
    data = r.json()
    opp = data.get("opportunity")
    typer.echo(json.dumps(opp, indent=2))


@APP.command()
def score(
    json_path: Path = typer.Option(..., "--json", exists=True, readable=True, help="Path to Opportunity JSON"),
    base: str = typer.Option(DEFAULT_BASE, help="Base URL for API"),
    raw: bool = typer.Option(False, "--raw", help="Print full response instead of just Decision Card"),
):
    """Score an Opportunity JSON and print the Decision Card."""
    try:
        opp = json.loads(json_path.read_text())
    except Exception as e:
        typer.echo(f"[error] failed to read JSON: {e}", err=True)
        raise typer.Exit(code=2)
    url = f"{base.rstrip('/')}/api/bid/score"
    try:
        r = requests.post(url, json=opp, timeout=60)
    except Exception as e:
        typer.echo(f"[error] request failed: {e}", err=True)
        raise typer.Exit(code=2)
    if not r.ok:
        typer.echo(f"[error] {r.status_code} {r.text}", err=True)
        raise typer.Exit(code=1)
    data = r.json()
    if raw:
        typer.echo(json.dumps(data, indent=2))
    else:
        card = data.get("Decision Card")
        typer.echo(json.dumps(card, indent=2))


def main():  # pragma: no cover
    APP()


if __name__ == "__main__":  # pragma: no cover
    main()
