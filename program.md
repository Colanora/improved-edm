# sampler-autoresearch

## program.md

This repo is an experiment in autonomous sampler research on a **fixed pre-trained diffusion model**.

The repo is already set up. Your job is **not** to build infrastructure, change evaluation, or retrain a model.  
Your job is to improve the **sampling trajectory** by editing **one file only**:

- `sample.py`

Everything else is frozen.

---

## Setup assumptions

Assume the following are already true:

1. the canonical checkpoint exists locally,
2. the FID reference stats exist locally,
3. the repo runs end-to-end,
4. the fixed baseline samplers are implemented,
5. `results.tsv` exists with the correct header.

If any of those assumptions fail, stop and tell the human exactly what is missing.

---

## What to read first

At the start of a fresh run, read these files in order:

1. `README.md`
2. `program.md`
3. `prepare.py`
4. `run.py`
5. `evaluate.py`
6. `sampler_protocol.py`
7. `sample.py`
8. `papers/manifest.yaml`
9. `results.tsv` (if it exists and is non-empty)

Do not spend time rereading the entire repo every iteration.  
After the first pass, focus on:

- `sample.py`
- recent results
- notes for the baseline you are trying to improve

---

## Experiment branch

Every new autonomous run should happen on a dedicated branch.

Suggested branch name:

- `autoresearch/<tag>`

Examples:

- `autoresearch/apr01`
- `autoresearch/apr01-gpu0`

Do not run the loop on `main`.

---

## The objective

The repo studies **fixed-NFE sample quality** on unconditional CIFAR-10 with a frozen EDM checkpoint.

The internal objective is:

- **lower `frontier_score` is better**

The frontier is defined on:

- `NFE = {5, 8, 10, 12}`

The paper metric is:

- **FID@50K** for each NFE

The daily search metric is:

- **proxy FID** on 5K images using the same evaluator stack

---

## What you can edit

You may edit only:

- `sample.py`

Inside `sample.py`, all of the following are fair game:

- the schedule law,
- the sigma reparameterization,
- local error estimators,
- stateful correction rules,
- predictor-corrector structure,
- trajectory smoothing,
- clamps and stabilizers,
- any small scalar hyperparameters local to the sampler.

---

## What you cannot edit

Do **not** edit:

- `prepare.py`
- `run.py`
- `evaluate.py`
- `model_adapter.py`
- `sampler_protocol.py`
- anything in `samplers/`
- `pyproject.toml`
- the checkpoint
- the FID reference statistics
- the evaluation split sizes
- the NFE frontier
- the result logging schema

Do **not** add dependencies.  
Do **not** retrain the diffusion model.  
Do **not** introduce trainable sampler parameters in v1.  
Do **not** change the benchmark to another dataset.

---

## Philosophy

This repo is not a sampler zoo.  
It is a **research loop**.

You are not trying to search all possible code paths.  
You are trying to discover a **better trajectory law**.

Prefer ideas that are:

- clear,
- explainable,
- local to the sampler,
- easy to ablate,
- cheap enough to re-run,
- grounded in the literature already tracked in `papers/manifest.yaml`.

Complexity matters.  
A tiny gain that makes `sample.py` ugly is usually not worth it.  
A tiny gain from a simpler sampler is a real win.

---

## First-run policy

On a fresh branch, the first task is always to establish the current state.

### Step 1

Confirm the current branch and commit.

### Step 2

Confirm `results.tsv` exists and has the expected header.

### Step 3

Run the frozen reference baselines on the proxy split if they are not already logged on this branch:

```bash
uv run run.py --sampler heun --split proxy > run_heun.log 2>&1
uv run run.py --sampler dpmpp --split proxy > run_dpmpp.log 2>&1
uv run run.py --sampler unipc --split proxy > run_unipc.log 2>&1
uv run run.py --sampler gits --split proxy > run_gits.log 2>&1
uv run run.py --sampler stork --split proxy > run_stork.log 2>&1
uv run run.py --sampler aflops --split proxy > run_aflops.log 2>&1
```

### Step 4

Run the current research sampler as-is:

```bash
uv run run.py --sampler research --split proxy > run_research.log 2>&1
```

### Step 5

Extract the metrics:

```bash
grep "^frontier_score:\|^fid_N\|^peak_vram_mb:" run_research.log
```

The initial unmodified `research` run is the baseline for the editable slot.

---

## Search splits

Use these three splits:

### `proxy`

- 5,000 samples
- default split for the main loop
- used for rapid keep/discard

### `confirm`

- 10,000 samples
- used only when a proxy improvement is small or noisy

### `final`

- 50,000 samples
- used for paper-quality numbers and periodic validation

The main loop should spend most of its time on `proxy`.

---

## Keep / discard rule

A change should be kept only if all of the following hold on the `proxy` split:

1. `frontier_score` improves, and
2. no individual NFE regresses by more than **3%**, and
3. the code remains reasonably simple.

### When improvement is small

If the proxy improvement is less than roughly **1.5%** in frontier score, treat it as uncertain.  
In that case, rerun the candidate on the `confirm` split before deciding.

### Confirmation rule

Keep the change if:

- `confirm` frontier score also improves, and
- no individual NFE regresses by more than **2%** on `confirm`.

If the proxy result improves but `confirm` does not, discard it.

---

## Main loop

LOOP FOREVER:

1. Look at the current git state.

2. Propose one concrete sampler idea.

3. Edit only `sample.py`.

4. Commit the change.

5. Run the proxy evaluation:

   ```bash
   uv run run.py --sampler research --split proxy > run.log 2>&1
   ```

6. Read out the result:

   ```bash
   grep "^frontier_score:\|^fid_N\|^peak_vram_mb:" run.log
   ```

7. If the grep output is empty, the run crashed:

   ```bash
   tail -n 50 run.log
   ```

8. Log the result to `results.tsv`.

9. Apply the keep/discard rule.

10. If the run is kept, advance the branch.

11. If the run is discarded, reset to the previous kept commit.

---

## Crash policy

If a run crashes:

1. inspect the last 50 log lines,
2. decide whether the crash is a trivial bug or a bad idea,
3. if trivial, fix and rerun,
4. if the idea is fundamentally unstable, mark it as `crash`, log it, revert, and move on.

Use:

- `0.000000` for `frontier_score`
- `0.0` for all FIDs
- `0.0` for VRAM
  in crash rows.

Do not get stuck retrying the same broken idea forever.

---

## Logging results

`results.tsv` is tab-separated with these columns:

```text
commit	sampler	split	frontier_score	fid_N5	fid_N8	fid_N10	fid_N12	peak_vram_mb	status	notes
```

Rules:

- one row per evaluation bundle,
- use `research` as the sampler name for the editable method,
- use `keep`, `discard`, or `crash`,
- keep notes short and concrete,
- do not commit `results.tsv` unless the human explicitly wants that.

Example:

```text
commit	sampler	split	frontier_score	fid_N5	fid_N8	fid_N10	fid_N12	peak_vram_mb	status	notes
a1b2c3d	research	proxy	1.932100	14.88	8.09	5.95	5.31	3011.7	keep	curvature-weighted schedule
b2c3d4e	research	proxy	1.945400	15.10	8.06	6.11	5.29	2988.2	discard	stronger corrector weight
c3d4e5f	research	proxy	0.000000	0.0	0.0	0.0	0.0	0.0	crash	NaN in adaptive step
```

---

## Allowed experiment directions

Good experiment families include:

- better time allocation laws,
- sigma-space reparameterization,
- local error proxies,
- curvature-aware schedules,
- trajectory smoothing,
- state averaging,
- dynamic corrector strength,
- order switching by region,
- cached warmup statistics,
- step-size damping,
- monotone correction rules,
- simplified versions of ideas from GITS, STORK, A-FloPS, ART-RL, or nearby schedule papers.

Especially good are ideas that:

- explain *why* a region of the trajectory is hard,
- change *where* solver effort is spent,
- or reduce error accumulation without touching model weights.

---

## Disallowed directions

Do not spend iterations on:

- arbitrary random hyperparameter fishing with no mechanism,
- changing file structure,
- new dependencies,
- changing the benchmark,
- training tiny side models,
- changing the FID implementation,
- changing seeds to cherry-pick wins,
- comparing only preview images and ignoring metrics.

---

## Periodic validation cadence

### Every 5 kept commits

Run:

```bash
uv run run.py --sampler research --split final --nfe 5,10 > run_final_short.log 2>&1
```

This is a short paper-quality sanity check at the most important low-NFE points.

### Every 10 kept commits

Run:

```bash
uv run run.py --sampler research --split final --nfe 5,8,10,12 > run_final_full.log 2>&1
```

This is the full paper frontier.

### Every 5 kept commits also export diagnostics

Export trajectory diagnostics for the current `research` sampler at:

- `NFE=10`
- `split=proxy`
- fixed diagnostic seeds

These are not the primary metric, but they are useful for understanding whether the mechanism makes sense.

---

## What counts as a good research idea

A good idea has all or most of these properties:

- it is visible in `sample.py`,
- it is explainable in one sentence,
- it changes the trajectory rather than the model,
- it can be ablated,
- it can be expressed as a small local change,
- it has a plausible mechanism.

Examples:

- “allocate smaller sigma jumps where coarse-vs-fine disagreement spikes”
- “blend predictor and corrector weights using a curvature proxy”
- “smooth the state only in late stiff regions”
- “use a warmup trajectory family to build one fixed schedule per NFE”

Bad ideas are usually:

- hard to explain,
- broad rewrites,
- or just random scalar sweeps without any hypothesis.

---

## Simplicity rule

All else equal:

- simpler is better,
- fewer moving parts is better,
- fewer hidden knobs is better.

A result that matches the current best while deleting complexity is a success.  
A result that improves by a tiny amount but turns `sample.py` into spaghetti is not.

---

## If you get stuck

If progress stalls:

1. look at the last 10 kept and discarded attempts,
2. identify which family of ideas keeps failing,
3. switch families,
4. revisit the strongest fixed baselines,
5. try a simpler version of a stronger method rather than a more complex version of a weak one.

Useful fallback moves:

- strip the current idea down,
- move more logic into the schedule and less into the step rule,
- or move more logic into the corrector and less into the schedule.

---

## Success criterion

The minimum success criterion for this repo is:

- `research` beats the best frozen baseline on the `final` frontier for at least one important low-NFE region, preferably NFE 5 and/or 8,
- under the fixed CIFAR-10 protocol,
- without changing the checkpoint or evaluator.

Stronger success:

- the improvement transfers across the full frontier,
- and the diagnostics suggest a clean mechanism rather than noise.

---

## Final reminder

This is a **frozen-model sampler research loop**.

Do not drift into:

- model training,
- benchmark redesign,
- evaluator redesign,
- or general framework engineering.

Read the repo, edit `sample.py`, run the experiment, keep or discard, repeat.