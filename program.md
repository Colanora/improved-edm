# Program

This repo exists to answer one question:

> For a fixed modern diffusion checkpoint on CIFAR-10, what sampling trajectory rules improve the fixed-NFE FID frontier under one common protocol?

## Frozen Contract
- Task: unconditional CIFAR-10 image generation at `32x32`
- Checkpoint: `edm-cifar10-32x32-uncond-vp.pkl`
- Final reported metric: `FID@50K`
- Search metric: `FID@5K`
- Frontier: `NFE = {5, 9, 11, 13}`
- Fixed runtime entrypoint: `run.py`
- Fixed setup entrypoint: `prepare.py`
- Fixed paper-comparable entrypoint: `paper_eval.py`
- Fixed sampler registry: `samplers/registry.py`
- Intended research edit surface after setup: `sample.py`
- Active verified baselines: `euler`, `heun`
- Upstream reference clone: `third_party/upstream-edm` (`NVLabs/edm`)

## Research Loop
1. Read the fixed docs and baseline modules.
2. Edit only `sample.py`.
3. Run `uv run run.py --sampler research --split proxy`.
4. Compare the frontier score and per-NFE FIDs against the current baseline.
5. Rerun promising changes on `confirm`, then `final`.
6. Keep or discard the change without changing the rest of the repo.

On this host, `ResearchSampler` is an EDM-Heun alias with upstream parity.

For paper-number claims, do not use the low-NFE frontier loop. Use `paper_eval.py`, which delegates to the official upstream generation and FID scripts with the paper-comparable 18-step configuration.

## Out of Scope
- Training or fine-tuning the model
- Changing model weights
- Distillation
- Guidance and conditional generation
- Switching checkpoints inside the main autoresearch loop
