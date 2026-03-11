# Frozen Sampler Autoresearch

Frozen-model sampler research substrate for EDM CIFAR-10 generation.

`sample.py` is the only intended future research edit surface. The authoritative evaluation path is [paper_eval.py](/home/wjy/scifi/autoresearch-sampler/paper_eval.py), which runs the official EDM paper-comparable generation flow through the local [paper_generate.py](/home/wjy/scifi/autoresearch-sampler/paper_generate.py) driver and the upstream EDM `fid.py`. The only frozen baselines are the official EDM ODE samplers `euler` and `heun`.

## Quick Start
```bash
export UV_INDEX_URL=https://mirrors.ustc.edu.cn/pypi/web/simple
uv sync
uv run prepare.py
uv run run.py --sampler research --split proxy
uv run paper_eval.py --sampler research --target uncond --gpus 1
uv run paper_eval.py --sampler heun --target cond --gpus 8
```

Optional mirror for users in mainland China:
```bash
export HF_ENDPOINT=https://hf-mirror.com
```

The first strict FID run also downloads the EDM Inception detector unless `EDM_INCEPTION_PATH` points to a local copy.

At baseline time, `sample.py` is an exact Heun alias, so `paper_eval.py --sampler research --target uncond` reproduces the official EDM Heun path.

## Canonical Protocol
- Checkpoint: `assets/checkpoints/edm-cifar10-32x32-uncond-vp.pkl`
- Authoritative target: unconditional CIFAR-10 on the official EDM paper path
- Authoritative metric: minimum FID across `3 x 50K` runs
- Auxiliary proxy: local frontier on `proxy=5K`, `confirm=10K`, `final=50K`
- Auxiliary frontier: `NFE = {5, 9, 11, 13}`
- Auxiliary keep/discard score: weighted log-FID frontier score

For `heun`, the NFE values are actual model evaluations. This matches upstream EDM exactly, so the underlying EDM step counts are `(NFE + 1) / 2`.

## Commands
```bash
uv run prepare.py --check
uv run run.py --sampler heun --split proxy
uv run run.py --sampler euler --split proxy
uv run run.py --sampler research --split confirm --nfe 5,9,11,13
uv run paper_eval.py --sampler research --target uncond --gpus 1
uv run paper_eval.py --sampler heun --target uncond --gpus 1
uv run paper_eval.py --sampler heun --target cond --gpus 8
```

## Paper Mode
- `paper_eval.py --sampler research --target uncond` is the authoritative autoresearch path.
- `paper_eval.py --sampler heun --target uncond` and `--sampler euler --target uncond` are frozen official baselines.
- `paper_eval.py --sampler heun --target cond` remains available for validating the official class-conditional paper path.
- `paper_results.tsv` stores authoritative paper-path runs, while `results.tsv` stores the auxiliary local frontier loop.

## Evaluation Splits
- `proxy`: 5,000 generated images with fixed seeds
- `confirm`: 10,000 generated images with fixed seeds
- `final`: 50,000 generated images with fixed seeds

All splits use the same evaluator implementation and the same CIFAR-10 reference stats file. Only the seed range and image count change.
