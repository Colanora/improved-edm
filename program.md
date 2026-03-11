# sampler-autoresearch

This repo is an experiment in autonomous sampler research on a fixed pre-trained EDM CIFAR-10 model.

The authoritative evaluation path is the official EDM paper path. The repo keeps a fast local loop for sanity checks, but paper-path results are the source of truth.

Your job is to improve the sampling trajectory by editing one file only:

- `sample.py`

Everything else is frozen infrastructure.

## Setup assumptions

Assume the following are already true:

1. the canonical unconditional checkpoint exists locally,
2. the FID reference stats exist locally,
3. the repo runs end-to-end,
4. the fixed EDM baseline samplers are implemented,
5. `results.tsv` exists with the correct header,
6. the local upstream EDM clone exists under `third_party/upstream-edm`.

If any of those assumptions fail, stop and tell the human exactly what is missing.

## What to read first

At the start of a fresh run, read these files in order:

1. `README.md`
2. `program.md`
3. `prepare.py`
4. `paper_eval.py`
5. `paper_generate.py`
6. `run.py`
7. `evaluate.py`
8. `sampler_protocol.py`
9. `sample.py`
10. `results.tsv` and `paper_results.tsv` if they exist and are non-empty

Do not spend time rereading the entire repo every iteration.

## The objective

The repo studies sampler behavior for a frozen EDM CIFAR-10 checkpoint.

There are two loops:

- Authoritative loop: `paper_eval.py`
- Auxiliary loop: `run.py`

The authoritative keep/discard decision comes from `paper_eval.py` on the official paper-comparable path.

The auxiliary loop exists only to catch obvious failures and get faster local signal.

## Authoritative path

Use `paper_eval.py` for any result that matters.

Current v1 research target:

- target: `uncond`
- sampler under edit: `research`
- baseline paper-equivalent sampler: `heun`
- official setting: `18` EDM steps
- reported metric: minimum FID across `3 x 50K` runs

At baseline time, `research` must reproduce the official EDM Heun result exactly.

## Auxiliary path

Use `run.py` only as a local proxy loop.

- split sizes: `proxy=5K`, `confirm=10K`, `final=50K`
- local frontier: `NFE = {5, 9, 11, 13}`
- lower `frontier_score` is better

These NFE values are actual model evaluations, not abstract step counts.

## What you can edit

You may edit only:

- `sample.py`

Inside `sample.py`, all sampler-local behavior is fair game:

- schedule law
- sigma reparameterization
- local correction rules
- stabilizers and clamps
- small scalar hyperparameters
- the mapping between local proxy NFE and paper-path steps

## What you cannot edit

Do not edit:

- `prepare.py`
- `paper_eval.py`
- `paper_generate.py`
- `run.py`
- `evaluate.py`
- `model_adapter.py`
- `sampler_protocol.py`
- anything in `samplers/`
- `pyproject.toml`
- the checkpoint
- the FID reference statistics
- the split sizes
- the result logging schemas

Do not add dependencies.
Do not retrain the diffusion model.
Do not introduce trainable sampler parameters.
Do not change the benchmark to another dataset.

## Baselines

The frozen baseline samplers are:

- `heun`
- `euler`

`research` starts as an exact Heun alias through `sample.py`.

## Acceptance rule

A change matters only if:

1. it remains simple enough to justify,
2. it survives the local proxy loop,
3. it improves or matches the authoritative paper-path outcome.

If the local proxy looks better but the paper path does not, discard the change.
