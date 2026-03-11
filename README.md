# Frozen Sampler Autoresearch

Frozen-model sampler research substrate for unconditional CIFAR-10 generation with the EDM checkpoint `edm-cifar10-32x32-uncond-vp.pkl`.

Only `sample.py` is intended for future research edits after setup. Everything else is the fixed protocol: one checkpoint, one evaluator stack, one NFE frontier, and one runtime loop.
The only implemented baselines are the official EDM ODE samplers: `euler` and `heun`. Behavior is checked against a local clone of `NVLabs/edm` at `third_party/upstream-edm`.
For paper-comparable claims, use [paper_eval.py](/home/wjy/scifi/autoresearch-sampler/paper_eval.py), which wraps the cloned upstream `generate.py` and `fid.py`.

## Quick Start
```bash
export UV_INDEX_URL=https://mirrors.ustc.edu.cn/pypi/web/simple
uv sync
uv run prepare.py
uv run run.py --sampler heun --split proxy
uv run run.py --sampler research --split proxy
uv run paper_eval.py --target cond --gpus 8
```

Optional mirror for users in mainland China:
```bash
export HF_ENDPOINT=https://hf-mirror.com
```

The first strict FID run also downloads the EDM Inception detector unless `EDM_INCEPTION_PATH` points to a local copy.

`sample.py` is currently a runnable alias of the upstream-parity Heun baseline.

## Canonical Protocol
- Checkpoint: `assets/checkpoints/edm-cifar10-32x32-uncond-vp.pkl`
- Final truth metric: `FID@50K`
- Search proxy: `FID@5K`
- Confirmation split: `FID@10K`
- Frontier: `NFE = {5, 9, 11, 13}`
- Internal keep/discard score: weighted log-FID frontier score

For `heun`, the NFE values are actual model evaluations. This matches upstream EDM exactly, so the underlying EDM step counts are `(NFE + 1) / 2`.

## Commands
```bash
uv run prepare.py --check
uv run run.py --sampler heun --split proxy
uv run run.py --sampler euler --split proxy
uv run run.py --sampler research --split confirm --nfe 5,9,11,13
uv run paper_eval.py --target uncond --gpus 1
uv run paper_eval.py --target cond --gpus 8
```

## Paper Mode
- `paper_eval.py --target cond` runs the official class-conditional CIFAR-10 paper path.
- `paper_eval.py --target uncond` runs the official unconditional CIFAR-10 paper path.
- It uses the cloned upstream repo under `third_party/upstream-edm`, fixed `18`-step EDM sampling, three `50K` seed blocks, and reports the minimum FID across the three runs in `paper_results.tsv`.

## Evaluation Splits
- `proxy`: 5,000 generated images with fixed seeds
- `confirm`: 10,000 generated images with fixed seeds
- `final`: 50,000 generated images with fixed seeds

All splits use the same evaluator implementation and the same CIFAR-10 reference stats file. Only the seed range and image count change.
