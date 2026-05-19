# chess-zero

AlphaZero-style chess engine and self-play RL pipeline built from scratch.

- Own chess board (no external chess libraries in main code)
- No supervised bootstrap; learns from rules + win/draw/loss only
- Mac-first; cloud burst when bottlenecked
- Public build-in-public on [serkan.ai/projects/chess-zero](https://serkan.ai/projects/chess-zero)

## Status

Scaffold stage. See [serkan.ai/journal/starting-chess-zero](https://serkan.ai/journal/starting-chess-zero) for the kickoff note and the project page for the current roadmap.

## Development

```bash
uv sync --all-extras

uv run pytest
uv run ruff check
uv run mypy
```

`python-chess` is allowed only inside `tests/oracles/` as a perft oracle. A `conftest.py` guard fails CI if `chess_zero/` ever imports it.

## License

MIT — see [LICENSE](LICENSE).
