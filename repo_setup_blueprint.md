
# Frozen Sampler Autoresearch on CIFAR-10
## Repo Setup Blueprint (build once, then freeze)

This document specifies how to build the **entire repository** for an autoresearch-style project whose job is to discover **better sampling trajectories** for a **fixed pre-trained diffusion model** on **CIFAR-10 unconditional generation**.

After setup is complete, the repo should behave like a Karpathy-style autoresearch substrate:

- one canonical checkpoint
- one canonical evaluation protocol
- one canonical runtime budget
- one canonical editable file: `sample.py`

Everything else should be frozen.

---

## 1. Project goal

Build a **lightweight, self-contained codebase** for **frozen-model sampler research**.

The repo should let an agent:

1. read the in-scope docs and code,
2. edit **only** `sample.py`,
3. run a fixed-budget experiment,
4. evaluate against a fixed CIFAR-10 protocol,
5. keep or discard the change,
6. iterate.

The repo is **not** for training a new diffusion model, training a flow model, or changing model weights.

---

## 2. Fixed design decisions

### 2.1 Canonical task
- **Task:** unconditional CIFAR-10 image generation
- **Resolution:** 32×32
- **Model family:** diffusion ODE sampling
- **Checkpoint:** fixed, pre-trained, frozen

### 2.2 Canonical checkpoint
Use this as the **default checkpoint**:

- `edm-cifar10-32x32-uncond-vp.pkl`

Why this one:
- it is an official checkpoint from the EDM codebase,
- it is widely reused by later sampler papers on CIFAR-10,
- it keeps the protocol aligned with the modern diffusion-solver literature.

Optional secondary checkpoint for sanity checks only:
- `baseline-cifar10-32x32-uncond-vp.pkl`

Do **not** make multiple checkpoints part of the main autoresearch loop in v1. One checkpoint keeps the protocol clean.

### 2.3 Canonical primary metric
The **paper metric** and final truth metric is:

- **FID on 50,000 generated images** against the CIFAR-10 reference statistics

### 2.4 Canonical search metric
The **autoresearch metric** should be a faster proxy computed with the **same evaluator stack**:

- **FID on 5,000 generated images**
- same Inception implementation
- same CIFAR-10 reference statistics
- fixed seed range

This is a **search proxy**, not the final paper number.

### 2.5 Canonical NFE frontier
Use this as the main few-step frontier:

- **NFE = {5, 8, 10, 12}**

These four budgets are enough to expose low-step behavior while still being cheap enough for repeated iteration.

### 2.6 Canonical aggregate score
For keep/discard decisions, define an internal scalar only for the agent loop:

\[
\text{FrontierScore}
=
\sum_{n \in \{5,8,10,12\}} w_n \log(\text{FID}_n + 10^{-8})
\]

with default weights

- `w_5 = 0.35`
- `w_8 = 0.30`
- `w_10 = 0.20`
- `w_12 = 0.15`

Lower is better.

This is an **internal repo score**.  
For papers, always report the raw per-NFE FIDs.

---

## 3. Scope boundaries

### 3.1 What is in scope
- ODE samplers
- predictor-corrector variants
- time/sigma schedule design
- local error control
- trajectory smoothing/correction
- stateful but training-free sampling logic
- warmup-based schedule search
- small fixed caches or warmup statistics

### 3.2 What is out of scope for v1
- training or fine-tuning the diffusion model
- distillation
- classifier guidance
- text-to-image evaluation
- changing the checkpoint during autoresearch
- flow-matching-specific repos/checkpoints
- methods whose main objective is wall-clock speedup through speculative skipping rather than fixed-NFE sample quality

---

## 4. Which papers to reproduce

The repo should not try to swallow every recent sampler paper at once.  
It should reproduce the methods that fit the **same protocol**:

- frozen model
- CIFAR-10 unconditional
- fixed-NFE quality evaluation
- no retraining
- easy mapping into a common sampler API

## 4.1 Required v1 reference set

### A. Canonical baseline / foundation
1. **EDM (Karras et al., 2022)**
   - Euler
   - Heun
   - Karras / EDM schedule variants
   - purpose: canonical model + canonical evaluator + simplest baseline

### B. Strong widely used solver baselines
2. **DPM-Solver++**
3. **UniPC**
4. **DEIS**
5. **iPNDM**

These are core reference samplers. The codebase is incomplete without them.

### C. Schedule / trajectory structure baselines
6. **GITS**  
   Geometric-regularity / dynamic-programming time schedule

### D. Strong modern training-free solver baseline
7. **STORK**

### E. Strong recent path-reparameterization baseline
8. **A-FloPS**

That is the recommended **minimum serious reproduction set**.

## 4.2 Optional v1.5 / phase-2 additions
These fit the same general protocol but are not necessary for the first clean build:

9. **ART-RL**  
   RL-based timestep schedule search

10. **S4S**  
    Solver-search / optimized solver family

These are good to add only after the v1 protocol is stable.

## 4.3 Explicitly do not force into v1
Do not make these mandatory for the first repo version:

- **FlowCast**
- **FastFlow**
- **TORS**
- **ERK-Guid**
- **Look-Ahead / Look-Back trajectory smoothing**

Reason:
- some of them are centered on **flow matching** rather than the EDM diffusion checkpoint,
- some are centered on **text-to-image** rather than CIFAR-10,
- some are centered on **guidance / conditional generation**,
- some optimize a **speed-quality tradeoff** instead of a clean fixed-NFE quality frontier.

Keep them in `papers/manifest.yaml` as inspiration, but do not let them distort the first repo.

---

## 5. The paper folder policy

The repo should include paper organization because the whole point is “read paper, reproduce method, normalize to one protocol”.

Recommended structure:

```text
papers/
├── manifest.yaml
├── raw/
└── notes/
```

### `papers/manifest.yaml`
Track every paper in a structured way:

```yaml
- id: karras2022_edm
  title: Elucidating the Design Space of Diffusion-Based Generative Models
  paper_url: https://arxiv.org/abs/2206.00364
  code_url: https://github.com/NVlabs/edm
  kind: canonical_model_and_sampler
  training_free: true
  fits_protocol: true
  status: implemented
  module: samplers/heun.py
  notes_file: papers/notes/karras2022_edm.md
```

### `papers/raw/`
Put the original PDFs here if you want local offline access.  
If repo size matters, make this directory optional or Git LFS-backed.

### `papers/notes/`
For each paper, create one markdown note that includes:
- equations actually used,
- mapping to our API,
- deviations from the paper,
- expected behavior,
- sanity-check results,
- why it is or is not in the main loop.

---

## 6. Canonical repo tree

```text
sampler-autoresearch/
├── README.md
├── program.md
├── pyproject.toml
├── prepare.py
├── run.py
├── evaluate.py
├── model_adapter.py
├── sampler_protocol.py
├── sample.py                    # ONLY editable file after setup
├── results.tsv
├── samplers/
│   ├── __init__.py
│   ├── registry.py
│   ├── euler.py
│   ├── heun.py
│   ├── dpmpp.py
│   ├── unipc.py
│   ├── deis.py
│   ├── ipndm.py
│   ├── gits.py
│   ├── stork.py
│   └── aflops.py
├── third_party/
│   └── edm/
│       ├── dnnlib/
│       ├── torch_utils/
│       └── minimal_fid/
├── papers/
│   ├── manifest.yaml
│   ├── raw/
│   └── notes/
├── assets/
│   ├── checkpoints/
│   ├── fid_refs/
│   ├── warmup/
│   ├── previews/
│   └── eval_cache/
└── artifacts/
    ├── logs/
    ├── diagnostics/
    └── samples/
```

---

## 7. File-by-file coding contract

## 7.1 `README.md`
Purpose:
- quick start,
- explain frozen-model sampler research,
- list the canonical checkpoint,
- explain proxy vs final metrics,
- explain that only `sample.py` is editable after setup,
- document the exact commands to run.

Must include:
- 5 command quick start,
- mirror instructions for mainland China,
- short explanation of the evaluation splits.

Keep it short and operational.

---

## 7.2 `pyproject.toml`
Use `uv` for dependency management.

Recommended dependencies:
- `python >=3.10`
- `torch`
- `torchvision`
- `numpy`
- `scipy`
- `pillow`
- `tqdm`
- `pyyaml`
- `matplotlib` (for diagnostics only)
- `huggingface_hub` (for mirrored asset download)

Do **not** depend on diffusers, accelerate, clean-fid, or giant general-purpose training stacks in v1.

The repo should stay lightweight.

---

## 7.3 `prepare.py` (fixed)
This is the one-time setup file.

Responsibilities:
1. create the directory tree,
2. verify Python / CUDA / torch availability,
3. download the checkpoint,
4. download the FID reference stats,
5. optionally mirror or cache the in-scope papers,
6. create `results.tsv` with the header row,
7. write fixed seed files for `proxy`, `confirm`, and `final`,
8. optionally precompute warmup caches for GITS-like methods.

Suggested CLI:
```bash
uv run prepare.py
uv run prepare.py --check
uv run prepare.py --download-only
uv run prepare.py --warmup
```

### What `prepare.py` should write
- `assets/checkpoints/edm-cifar10-32x32-uncond-vp.pkl`
- `assets/fid_refs/cifar10-32x32.npz`
- `assets/eval_cache/seeds_proxy.txt`
- `assets/eval_cache/seeds_confirm.txt`
- `assets/eval_cache/seeds_final.txt`
- `results.tsv` if missing

### What `prepare.py` must not do
- no experiments
- no baseline runs
- no editable research logic

---

## 7.4 `model_adapter.py` (fixed)
This file wraps the EDM checkpoint into a clean, repo-local interface.

Implement a single adapter class:

```python
class EDMAdapter:
    def __init__(self, checkpoint_path: str, device: torch.device): ...
    def sigma_min(self) -> float: ...
    def sigma_max(self) -> float: ...
    def round_sigma(self, sigma: torch.Tensor) -> torch.Tensor: ...
    def denoise(self, x: torch.Tensor, sigma: torch.Tensor) -> torch.Tensor: ...
    def score(self, x: torch.Tensor, sigma: torch.Tensor) -> torch.Tensor: ...
    def x0(self, x: torch.Tensor, sigma: torch.Tensor) -> torch.Tensor: ...
    def velocity(self, x: torch.Tensor, sigma: torch.Tensor) -> torch.Tensor: ...
```

Goals:
- hide checkpoint loading details,
- hide EDM-specific persistence logic,
- give all samplers one consistent interface.

Do not let individual sampler implementations load the model themselves.

---

## 7.5 `sampler_protocol.py` (fixed)
This file defines the common sampler API.

Recommended contents:
- dataclasses for run config and eval config,
- a `SamplerContext`,
- a `SamplerOutput`,
- helper functions for sigma schedules and NFE accounting.

Recommended interface:

```python
@dataclass
class SamplerConfig:
    nfe: int
    sigma_min: float
    sigma_max: float
    seed: int
    device: str
    extra: dict[str, Any]

@dataclass
class SamplerOutput:
    images: torch.Tensor
    nfe_used: int
    trace: Optional[dict[str, torch.Tensor]]
    aux: dict[str, Any]

class BaseSampler(Protocol):
    name: str
    def sample(self, adapter: EDMAdapter, z: torch.Tensor, cfg: SamplerConfig) -> SamplerOutput: ...
```

Why:
- every baseline and the editable research sampler should satisfy the same interface,
- `run.py` and `evaluate.py` should never care which sampler produced the images.

---

## 7.6 `samplers/registry.py` (fixed)
This file maps sampler names to implementations.

Example:
```python
BUILTIN_SAMPLERS = {
    "euler": EulerSampler,
    "heun": HeunSampler,
    "dpmpp": DPMSolverPPSampler,
    "unipc": UniPCSampler,
    "deis": DEISSampler,
    "ipndm": IPNDMSampler,
    "gits": GITSSampler,
    "stork": STORKSampler,
    "aflops": AFloPSSampler,
    "research": ResearchSampler,  # imported from sample.py
}
```

Do not edit this file after setup unless the repo itself is broken.

---

## 7.7 `samplers/*.py` (fixed)
Each reference method gets its own file.

This is important.  
Do **not** put all reference solvers into one giant file.

### `samplers/euler.py`
- vanilla first-order sampler
- minimal baseline
- exact NFE accounting
- no hidden tricks

### `samplers/heun.py`
- EDM-style deterministic Heun baseline
- this should be the simplest strong baseline

### `samplers/dpmpp.py`
- DPM-Solver++ reference implementation
- keep only the variant you intend to benchmark
- recommended default: a single strong ODE variant, not the entire family zoo

### `samplers/unipc.py`
- UniPC reference implementation
- one strong published configuration only

### `samplers/deis.py`
- DEIS reference implementation
- same principle: one clean variant

### `samplers/ipndm.py`
- iPNDM reference implementation

### `samplers/gits.py`
Should include:
- warmup trajectory generation,
- curvature- or local-error-based timestamp scoring,
- dynamic-programming schedule search,
- cached schedules by NFE.

Important:
- keep the warmup cache logic outside `sample.py`,
- the main loop should be able to reuse cached schedules.

### `samplers/stork.py`
Should include:
- the solver update rule,
- any fixed coefficients,
- a small number of exposed constants,
- exact NFE accounting.

### `samplers/aflops.py`
Should include:
- path reparameterization,
- decomposition logic,
- fixed configuration from the paper.

Keep the reference implementation faithful and frozen.

---

## 7.8 `sample.py` (ONLY editable file after setup)
This is the **research slot**.

Initial content:
- start from a copy of the strongest fixed v1 method that reproduces cleanly on the repo protocol,
- expose it as `ResearchSampler`,
- keep the structure readable enough that an agent can mutate the schedule law, correction rule, or local state update.

Recommended shape:

```python
class ResearchSampler:
    name = "research"

    def __init__(self):
        ...

    def build_schedule(self, adapter, cfg):
        ...

    def init_state(self, adapter, z, sigmas, cfg):
        ...

    def step(self, adapter, x, i, sigmas, state, cfg):
        ...

    def sample(self, adapter, z, cfg):
        ...
```

The agent should be able to iterate by touching only:
- schedule construction,
- state initialization,
- one-step update logic,
- small scalar constants.

Do not make `sample.py` responsible for:
- logging,
- FID evaluation,
- checkpoint loading,
- CLI parsing,
- file I/O for the experiment loop.

---

## 7.9 `evaluate.py` (fixed)
Responsibilities:
1. compute proxy FID,
2. compute final FID,
3. compute internal frontier score,
4. optionally compute trajectory diagnostics,
5. write small preview grids.

### Primary evaluation functions
```python
def calc_fid(images: torch.Tensor, ref_npz_path: str) -> float: ...
def calc_frontier(fid_by_nfe: dict[int, float]) -> float: ...
```

### Split definitions
Use three fixed splits:

- `proxy`: 5,000 images
- `confirm`: 10,000 images
- `final`: 50,000 images

All three splits should use:
- the same evaluator implementation,
- the same reference statistics,
- different fixed seed ranges.

### Important rule
Trajectory metrics are **diagnostics only** in v1.  
Do not let them replace FID as the main keep/discard criterion.

### Optional diagnostics
These are useful, but secondary:
- projected trajectory length
- curvature statistics
- torsion statistics
- coarse-vs-fine solver discrepancy
- state norm / x0 drift profiles

Write them to JSON under:
- `artifacts/diagnostics/<commit>/<sampler>/<split>/`

---

## 7.10 `run.py` (fixed)
This is the one command the agent runs during research.

Responsibilities:
1. parse CLI,
2. load the adapter,
3. instantiate the sampler,
4. evaluate a full NFE frontier,
5. print grep-friendly summary lines,
6. optionally save preview images.

Recommended CLI:
```bash
uv run run.py --sampler research --split proxy
uv run run.py --sampler heun --split proxy
uv run run.py --sampler stork --split final
uv run run.py --sampler research --split confirm --nfe 5,8,10,12
```

Recommended printed output:
```text
sampler: research
split: proxy
frontier_score: 1.234567
fid_N5: 8.1234
fid_N8: 4.5678
fid_N10: 3.9876
fid_N12: 3.6543
runtime_s: 291.2
peak_vram_mb: 3124.0
```

This exact format matters because the agent can parse it with `grep`.

---

## 7.11 `results.tsv` (fixed schema)
Use one row per **evaluation bundle**.

Recommended columns:
```text
commit	sampler	split	frontier_score	fid_N5	fid_N8	fid_N10	fid_N12	peak_vram_mb	status	notes
```

Status must be one of:
- `keep`
- `discard`
- `crash`

Example:
```text
commit	sampler	split	frontier_score	fid_N5	fid_N8	fid_N10	fid_N12	peak_vram_mb	status	notes
a1b2c3d	heun	proxy	1.987654	15.23	8.41	6.17	5.52	2890.4	keep	baseline
b2c3d4e	research	proxy	1.932100	14.88	8.09	5.95	5.31	3011.7	keep	curvature-weighted schedule
c3d4e5f	research	proxy	0.000000	0.0	0.0	0.0	0.0	0.0	crash	bad state update NaN
```

Do not commit `results.tsv` if you want a clean git history.  
But keep it present locally.

---

## 8. China-friendly setup and download policy

The repo should be easy to set up in mainland China.

## 8.1 Python package mirror with USTC + uv
Create `~/.config/uv/uv.toml`:

```toml
[[index]]
url = "https://mirrors.ustc.edu.cn/pypi/simple"
default = true
```

This is the recommended default package mirror for `uv`.

## 8.2 Optional Conda bootstrap via USTC
If you need Miniconda first, use the USTC Miniconda / conda-forge mirror.
Do not make Conda a hard dependency for the repo itself.

## 8.3 Hugging Face mirror
Set:

```bash
export HF_ENDPOINT=https://hf-mirror.com
```

Use this for:
- mirrored asset repos you host yourself,
- any paper snapshots or auxiliary files you choose to host on HF,
- any later extension that relies on Hugging Face-hosted files.

## 8.4 Important note about the canonical checkpoint
The official EDM checkpoint is hosted on NVIDIA’s CDN, not on Hugging Face.

Therefore the clean setup policy is:

### Preferred policy
Create a tiny asset mirror repository on Hugging Face, for example:
- `your-org/sampler-autoresearch-assets`

Mirror into it:
- `edm-cifar10-32x32-uncond-vp.pkl`
- `cifar10-32x32.npz`
- optionally the baseline checkpoint too

Then users in China can download through `hf-mirror.com`.

### Example mirrored download commands
```bash
export HF_ENDPOINT=https://hf-mirror.com
huggingface-cli download your-org/sampler-autoresearch-assets edm-cifar10-32x32-uncond-vp.pkl --local-dir assets/checkpoints
huggingface-cli download your-org/sampler-autoresearch-assets cifar10-32x32.npz --local-dir assets/fid_refs
```

### Fallback official download commands
```bash
wget -O assets/checkpoints/edm-cifar10-32x32-uncond-vp.pkl \
  https://nvlabs-fi-cdn.nvidia.com/edm/pretrained/edm-cifar10-32x32-uncond-vp.pkl

wget -O assets/fid_refs/cifar10-32x32.npz \
  https://nvlabs-fi-cdn.nvidia.com/edm/fid-refs/cifar10-32x32.npz
```

## 8.5 Asset manifest
Create a small tracked manifest:
```yaml
checkpoint:
  filename: edm-cifar10-32x32-uncond-vp.pkl
  sha256: ...
  primary_url: https://nvlabs-fi-cdn.nvidia.com/edm/pretrained/edm-cifar10-32x32-uncond-vp.pkl
  mirror_repo: your-org/sampler-autoresearch-assets

fid_ref:
  filename: cifar10-32x32.npz
  sha256: ...
  primary_url: https://nvlabs-fi-cdn.nvidia.com/edm/fid-refs/cifar10-32x32.npz
  mirror_repo: your-org/sampler-autoresearch-assets
```

This avoids ambiguity forever.

---

## 9. How to code the evaluation protocol

## 9.1 Final evaluation
The canonical reported number is:

- `FID@50K` for each NFE in `{5, 8, 10, 12}`

This is what should appear in tables and plots.

## 9.2 Search evaluation
Use the exact same evaluator, but on 5K images.

That gives:
- same metric family,
- same reference statistics,
- lower runtime,
- far less protocol drift.

## 9.3 Confirmation evaluation
When a proxy result is close to the current best, rerun with:
- 10K images
- same NFE set

This guards against noisy keeps.

## 9.4 Diagnostics
Diagnostics should be exported but not used as the primary score in v1.

Recommended diagnostic pack:
- preview grid
- trajectory PCA projection
- path length
- curvature profile
- torsion profile
- coarse-vs-fine discrepancy

---

## 10. Baseline reproduction plan

## 10.1 Phase 0 — scaffold
Build first:
- directory tree
- `pyproject.toml`
- `prepare.py`
- `model_adapter.py`
- `sampler_protocol.py`
- `run.py`
- `evaluate.py`
- `results.tsv` header

Acceptance:
- `uv run prepare.py --check` passes
- `uv run run.py --sampler heun --split proxy` runs end-to-end

## 10.2 Phase 1 — foundational baselines
Implement:
- Euler
- Heun
- DPM-Solver++
- UniPC

Acceptance:
- each method runs under one unified API
- each method returns plausible FID ordering

## 10.3 Phase 2 — stronger reference baselines
Implement:
- DEIS
- iPNDM
- GITS

Acceptance:
- schedule search caches work
- repeat runs with the same seeds are stable

## 10.4 Phase 3 — modern stronger methods
Implement:
- STORK
- A-FloPS

Acceptance:
- methods fit the same fixed API
- results are logged under the same frontier protocol

## 10.5 Phase 4 — research slot
Copy the strongest clean baseline into `sample.py` as:
- `ResearchSampler`

From this point on:
- only `sample.py` is editable
- baselines stay frozen

---

## 11. Recommended tests before declaring setup complete

Run these in order:

```bash
uv sync
uv run prepare.py
uv run run.py --sampler heun --split proxy
uv run run.py --sampler dpmpp --split proxy
uv run run.py --sampler unipc --split proxy
uv run run.py --sampler gits --split proxy
uv run run.py --sampler stork --split proxy
uv run run.py --sampler research --split proxy
```

Setup is complete only if:
1. all commands finish,
2. `results.tsv` can be appended,
3. the printed summary is parseable,
4. `sample.py` is the only file needed for future research edits.

---

## 12. Recommended v1 research stance

Do not make the repo about “all sampler papers ever”.

Make the repo about this narrower question:

> For a fixed modern diffusion checkpoint on CIFAR-10, what sampling trajectory rules improve the fixed-NFE FID frontier under a single common protocol?

That is tight enough for autoresearch, but still open-ended enough for new theory.

---

## 13. Final recommendation

If you only build one first version, build **exactly this**:

- canonical checkpoint: `edm-cifar10-32x32-uncond-vp.pkl`
- canonical final metric: `FID@50K`
- canonical frontier: `NFE = {5, 8, 10, 12}`
- canonical editable file: `sample.py`
- frozen baselines:
  - Euler
  - Heun
  - DPM-Solver++
  - UniPC
  - DEIS
  - iPNDM
  - GITS
  - STORK
  - A-FloPS
- paper organization:
  - `papers/manifest.yaml`
  - `papers/raw/`
  - `papers/notes/`
- China-friendly setup:
  - `uv` + USTC mirror
  - Hugging Face mirror repo for the official EDM assets

That gives you a repo that is:
- small,
- reproducible,
- aligned with accepted CIFAR-10 sampler evaluation,
- and genuinely usable for autoresearch.
