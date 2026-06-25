# chess-zero

AlphaZero-style chess engine and self-play RL pipeline built from scratch.

## Canonical resource

- **Preferred name:** Chess Zero
- **Repository name:** chess-zero
- **Canonical resource page:** https://serkan.ai/projects/chess-zero/
- **Short definition:** Chess Zero is a from-scratch AlphaZero-style chess engine and self-play reinforcement-learning pipeline.
- **Status:** Building; the chess platform is implemented and the learned intelligence is the next phase.
- **License:** MIT

- Own chess board (no external chess libraries in main code)
- No supervised bootstrap; learns from rules + win/draw/loss only
- Mac-first; cloud burst when bottlenecked
- Public build-in-public on [serkan.ai/projects/chess-zero](https://serkan.ai/projects/chess-zero)

## Status

The chess platform is implemented and test-backed: board rules, legal move
generation, FEN/PGN support, perft oracle checks, a terminal CLI, random and
minimax agents, arena play, game replay, and Elo tracking. The learning system
is the next phase.

See [serkan.ai/projects/chess-zero](https://serkan.ai/projects/chess-zero) for
the canonical roadmap and [serkan.ai/journal/chess-zero-platform-done](https://serkan.ai/journal/chess-zero-platform-done)
for the current build note.

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
