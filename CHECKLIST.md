# chess-zero — checklist

Canonical step list, mirroring the roadmap on
[serkan.ai/projects/chess-zero](https://serkan.ai/projects/chess-zero).
Flip `- [ ]` to `- [x]` as steps land. Inline `> ...` quote lines under a
step are notes (measurements, decisions) — kept for future-me.

- [x] Brainstorm + design spec drafted
- [x] Repo scaffold (uv, pyproject, ruff, mypy, pytest, GitHub Actions CI)

- [x] Board representation, piece movement, pseudo-legal move generation
- [x] Legality (check, pin, mate, stalemate), castling, en passant, promotion
- [x] Draw rules (50-move, 3-fold repetition, insufficient material)
- [x] FEN and PGN parse/serialize
- [x] Perft suite against python-chess oracle (perft(4) green)
> python-chess lives in tests/oracles/ only; never imported by chess_zero/
> 6 standard positions × depth 1-3 + starting d4 = 19 cases, all match.
> Aliasing bug in `_king_moves` (queenside castle missed in Kiwipete) caught and fixed.
- [x] Interactive terminal CLI: play vs human, play vs random

- [x] Agent ABC + RandomAgent + Minimax baseline (handcrafted eval)
- [x] Arena (two agents, one game), Elo tracking, game-log replay
- [ ] Gauntlet runner: random vs minimax 100-game match

- [ ] Board → tensor encoding (12 piece planes + 7 meta channels)
- [ ] Value network (small ResNet), training pipeline, checkpoint manager
- [ ] NNAgent (1-ply lookahead with NN eval), gauntlet vs Random/Minimax
- [ ] Tracking infra: run_id, config snapshot, JSONL metric logger

- [ ] AlphaNet (combined policy + value head, ResNet body)
- [ ] Move encoding (action space → policy logits index) + illegal-move mask
- [ ] MCTS (PUCT, expansion, simulation, backup, Dirichlet noise at root)
- [ ] MCTSAgent + smoke gauntlet vs RandomAgent
- [ ] Config-driven hyperparam YAML, run resumability primitives

- [ ] Self-play generator (best agent vs self) + (state, π, z) emission
- [ ] Replay buffer (disk-backed JSONL shards, rolling window)
- [ ] Training loop: policy + value loss, optimizer, periodic checkpoints
- [ ] Orchestrator (selfplay → train → eval → promote, resumable)
- [ ] Promotion gate: new vs best 100-game arena, ≥55% promotion threshold
- [ ] First end-to-end smoke run + debug + stabilize
- [ ] Elo curve tracking + gauntlet vs Random/Minimax/older checkpoints
- [ ] Status export script + serkan.ai status auto-update integration

- [ ] Hyperparameter exploration (LR, MCTS sims, replay size, batch size)
- [ ] Architecture iteration (ResNet depth, channels), ablation runs
- [ ] Performance optimization (NumPy bitboards or Rust core)
> decided at the point Mac self-play throughput is the bottleneck, not before
- [ ] Cloud burst experiment (Modal/Lambda spot), measure $/Elo gained
- [ ] Extended training runs (>1M self-play games)

- [ ] Final gauntlet + Elo measurement + checkpoint comparison curve
- [ ] Repo polish: README, CONTRIBUTING, docs, type hints, lint clean
