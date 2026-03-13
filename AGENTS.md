# Repository Guidelines

## Project Structure & Module Organization
Top-level scripts drive the research workflow: `sample.py` is the preferred sampler edit surface, while `prepare.py`, `run.py`, `paper_generate.py`, `paper_eval.py`, and `evaluate.py` handle setup and evaluation. Core implementations live in `samplers/`, with shared protocol and adapter logic in `sampler_protocol.py` and `model_adapter.py`. Tests are under `tests/` with reusable fakes in `tests/fakes.py`. Static inputs live in `assets/`, generated outputs belong in `artifacts/`, vendored upstream EDM code is in `third_party/edm/`, and research notes/manifests are in `papers/` and `program.md`.

## Build, Test, and Development Commands
Use `uv` from the repository root because `[tool.uv].package = false`.

- `uv sync --extra dev` installs runtime and test dependencies.
- `uv run prepare.py` downloads or prepares checkpoints, seeds, and reference stats.
- `uv run prepare.py --check` verifies required assets without modifying them.
- `uv run pytest` runs the full test suite.
- `uv run run.py --sampler research --split proxy` runs the local frontier loop.
- `uv run paper_eval.py --sampler research --target uncond --gpus 1` runs the authoritative paper-path evaluation.

## Coding Style & Naming Conventions
Target Python 3.10+ with 4-space indentation and explicit type hints on public APIs. Follow existing naming: `snake_case` for modules, functions, and variables; `PascalCase` for classes; `UPPER_CASE` for constants. Keep CLI defaults and filesystem paths near module-level constants. Preserve the frozen baseline samplers in `samplers/euler.py` and `samplers/heun.py`; new research behavior should usually be introduced through `sample.py`.

## Testing Guidelines
Tests use `pytest` and should be named `tests/test_<feature>.py`. Prefer fast unit coverage built on the fake adapters and toy networks in `tests/fakes.py`. For sampler changes, verify protocol behavior such as `nfe_used`, split handling, and target support, then add parity or regression checks when behavior must stay aligned with EDM baselines. Run focused tests while iterating, then finish with `uv run pytest`.

## Commit & Pull Request Guidelines
Recent commits use short, imperative subjects such as `Test damped Heun research sampler`. Keep the subject specific and add body details when changing evaluation protocol, assets, or paper-path behavior. Pull requests should summarize scope, link relevant issues or research context, list exact validation commands, and call out any FID or frontier-score movement. Include preview grids or diagnostics when output behavior changes.

## Configuration & Assets
Use environment overrides such as `UV_INDEX_URL`, `HF_ENDPOINT`, or `EDM_INCEPTION_PATH` only in local setup; do not hardcode them. Do not commit generated artifacts, downloaded checkpoints, or detector files unless the repository explicitly tracks them.
