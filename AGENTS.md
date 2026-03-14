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

## Skills
A skill is a set of local instructions to follow that is stored in a `SKILL.md` file. Below is the list of skills that can be used. Each entry includes a name, description, and file path so you can open the source for full instructions when using a specific skill.
### Available skills
- skill-creator: Guide for creating effective skills. This skill should be used when users want to create a new skill (or update an existing skill) that extends Codex's capabilities with specialized knowledge, workflows, or tool integrations. (file: /root/.codex/skills/.system/skill-creator/SKILL.md)
- skill-installer: Install Codex skills into $CODEX_HOME/skills from a curated list or a GitHub repo path. Use when a user asks to list installable skills, install a curated skill, or install a skill from another repo (including private repos). (file: /root/.codex/skills/.system/skill-installer/SKILL.md)
### How to use skills
- Discovery: The list above is the skills available in this session (name + description + file path). Skill bodies live on disk at the listed paths.
- Trigger rules: If the user names a skill (with `$SkillName` or plain text) OR the task clearly matches a skill's description shown above, you must use that skill for that turn. Multiple mentions mean use them all. Do not carry skills across turns unless re-mentioned.
- Missing/blocked: If a named skill isn't in the list or the path can't be read, say so briefly and continue with the best fallback.
- How to use a skill (progressive disclosure):
  1) After deciding to use a skill, open its `SKILL.md`. Read only enough to follow the workflow.
  2) When `SKILL.md` references relative paths (e.g., `scripts/foo.py`), resolve them relative to the skill directory listed above first, and only consider other paths if needed.
  3) If `SKILL.md` points to extra folders such as `references/`, load only the specific files needed for the request; don't bulk-load everything.
  4) If `scripts/` exist, prefer running or patching them instead of retyping large code blocks.
  5) If `assets/` or templates exist, reuse them instead of recreating from scratch.
- Coordination and sequencing:
  - If multiple skills apply, choose the minimal set that covers the request and state the order you'll use them.
  - Announce which skill(s) you're using and why (one short line). If you skip an obvious skill, say why.
- Context hygiene:
  - Keep context small: summarize long sections instead of pasting them; only load extra files when needed.
  - Avoid deep reference-chasing: prefer opening only files directly linked from `SKILL.md` unless you're blocked.
  - When variants exist (frameworks, providers, domains), pick only the relevant reference file(s) and note that choice.
- Safety and fallback: If a skill can't be applied cleanly (missing files, unclear instructions), state the issue, pick the next-best approach, and continue.
