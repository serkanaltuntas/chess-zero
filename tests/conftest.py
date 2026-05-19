"""Shared test configuration. Enforces the chess-library boundary."""

from __future__ import annotations

import pathlib
import re

CHESS_IMPORT_RE = re.compile(r"^\s*(import\s+chess|from\s+chess(\.|$|\s))", re.M)


def pytest_collection_modifyitems(session, config, items):  # type: ignore[no-untyped-def]
    """Fail collection if chess_zero/ imports python-chess anywhere."""
    root = pathlib.Path(__file__).parent.parent / "chess_zero"
    for path in root.rglob("*.py"):
        text = path.read_text()
        if CHESS_IMPORT_RE.search(text):
            raise RuntimeError(
                f"BOUNDARY VIOLATION: {path} imports `chess`. "
                "`python-chess` is only allowed inside tests/oracles/."
            )
