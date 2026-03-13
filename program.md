# sampler-autoresearch

## program.md (revised)

This repo is an experiment in autonomous sampler research on a **fixed pre-trained diffusion model**.

The repo is already set up. Your job is **not** to build infrastructure, change evaluation, or retrain a model.
Your job is to improve the **sampling trajectory** by editing **one file only**:

- `sample.py`

Everything else is frozen.

---

## Why this revised protocol exists

The old loop over-weighted low-NFE proxy frontier wins and allowed the branch to drift away from the canonical EDM comparison.
A sampler that wins on `proxy` at `NFE={5,9,11,13}` but loses on the strict local EDM benchmark at `NFE=35` is **not** a stronger general result.

At the time of this revision, the known reference points are:

- current research sampler `b91fc7c` on `final`, `NFE=35`: **FID = 2.2485**
- official local EDM Heun on the same evaluator and split: **FID = 2.0073**
- EDM paper/reference number: **FID = 1.97**

Therefore, **proxy frontier gains do not automatically translate to the standard apples-to-apples protocol**.
This revised program hard-codes translation checks so that this failure mode cannot silently accumulate.

---

## Setup assumptions

Assume the following are already true:

1. the unconditional EDM checkpoint exists locally,
2. the CIFAR-10 FID reference stats exist locally,
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
10. `heun_final_nfe35.log` and `b91fc7c_research_final_nfe35.log` if they exist

Do not spend time rereading the entire repo every iteration.
After the first pass, focus on:

- `sample.py`
- recent results
- the current standard benchmark gap at `NFE=35`
- notes for the sampler family you are trying to improve

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

## Two scoreboards: exploration vs. ship metric

This repo now has **two** scoreboards.

### 1) Frontier scoreboard (exploration only)

This is the low-NFE frontier studied by the repo:

- `NFE = {5, 9, 11, 13}`
- metric: **lower `frontier_score` is better**
- final metric on this track: **FID@50K** on the `final` split for each frontier NFE
- daily search metric on this track: **proxy FID** on 5K images using the same evaluator stack

### 2) Standard scoreboard (ship / claim metric)

This is the canonical local EDM benchmark and the source of truth for claims:

- `NFE = 35`
- this corresponds to the canonical **18-step EDM Heun regime**
- split sizes are still `proxy`, `confirm`, and `final`
- final ship metric: **FID@50K at NFE=35**
- baseline to beat locally: **official EDM Heun under the same local evaluator**

### Important rule

A sampler that improves the frontier scoreboard but does not improve, or at least preserve, the standard scoreboard is **not** a branch champion.
It may be a frontier-only curiosity, but it must not replace the standard-qualified base commit.

### Source of truth for comparisons

Use the following precedence:

1. **local official EDM Heun under this repo and evaluator**
2. current best **research** commit under the same local evaluator
3. paper/reference EDM number for context only

Do **not** use the paper number as the keep/discard baseline if the local evaluator differs slightly.
The local Heun run is the apples-to-apples comparator.

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
- the frontier NFE set
- the standard apples-to-apples benchmark at `NFE=35`

Do **not** add dependencies.
Do **not** retrain the diffusion model.
Do **not** introduce trainable sampler parameters in v1.
Do **not** change the benchmark to another dataset.
Do **not** change the local Heun comparator.

---

## Philosophy

This repo is not a sampler zoo.
It is a **research loop with translation discipline**.

You are not trying to search all possible code paths.
You are trying to discover a **better trajectory law** that survives both:

- low-NFE frontier evaluation, and
- the canonical local EDM comparison at `NFE=35`.

Prefer ideas that are:

- clear,
- explainable,
- local to the sampler,
- easy to ablate,
- cheap enough to re-run,
- grounded in the literature already tracked in `papers/manifest.yaml`,
- and plausible across more than one NFE regime.

Complexity matters.
A tiny gain that makes `sample.py` ugly is usually not worth it.
A tiny gain from a simpler sampler is a real win.
A frontier-only gain that increases the standard benchmark gap is **not** a win.

---

## New anti-drift rules

These rules exist specifically to prevent endless proxy tuning that does not translate.

### Rule A: proxy is a screen, not a claim

A `proxy` win is only a reason to continue testing.
A `proxy` win is **not** sufficient evidence that the branch should advance.

### Rule B: every frontier test must be paired with a standard translation check

Any candidate evaluated on the frontier must also be evaluated at `NFE=35` on the same split tier before it can be kept.

That means:

- frontier `proxy` -> must pair with standard `proxy` at `NFE=35`
- frontier `confirm` -> must pair with standard `confirm` at `NFE=35`
- periodic frontier `final` -> must pair with standard `final` at `NFE=35`

### Rule C: no branch advancement from frontier-only keeps

Keep two commit pointers mentally or in notes:

- `last_frontier_keep`
- `last_standard_keep`

Only `last_standard_keep` is allowed to serve as the base for the next serious experiment.
If a candidate wins frontier but fails the standard translation gate, reset to `last_standard_keep`, not to the latest frontier-only keep.

### Rule D: no endless same-family scalar twiddling

No more than **2 consecutive kept commits** may be scalar-only tuning changes inside the same mechanism family.
Examples of scalar-only tuning include:

- nudging one schedule exponent,
- moving one split point,
- adjusting one fixed corrector weight,
- changing a single bracket threshold.

After 2 such keeps, the next iteration must do one of the following:

- switch to a different mechanism family,
- add an ablation that tests the claimed mechanism,
- or revert to the last standard-qualified commit and start a new idea.

A third consecutive scalar-only keep in the same family is not allowed.

### Rule E: if standard regression appears twice, retire the family

If the same mechanism family produces **two separate candidates** that improve frontier but fail the standard translation gate, retire that family for the current run.
Move on.

---

## First-run policy

On a fresh branch, the first task is always to establish the current state.

### Step 1

Confirm the current branch and commit.

### Step 2

Confirm `results.tsv` exists and has the expected header.

### Step 3

Establish the immutable local apples-to-apples comparator at `NFE=35` if it is not already logged for this environment:

```bash
uv run run.py --sampler heun --split proxy --nfe 35 > heun_proxy_nfe35.log 2>&1
uv run run.py --sampler heun --split confirm --nfe 35 > heun_confirm_nfe35.log 2>&1
uv run run.py --sampler heun --split final --nfe 35 > heun_final_nfe35.log 2>&1
```

Extract the metrics:

```bash
grep "^start_time_utc:\|^end_time_utc:\|^nfe_.*runtime_s:\|^fid_N\|^runtime_s:\|^peak_vram_mb:" heun_proxy_nfe35.log
grep "^start_time_utc:\|^end_time_utc:\|^nfe_.*runtime_s:\|^fid_N\|^runtime_s:\|^peak_vram_mb:" heun_confirm_nfe35.log
grep "^start_time_utc:\|^end_time_utc:\|^nfe_.*runtime_s:\|^fid_N\|^runtime_s:\|^peak_vram_mb:" heun_final_nfe35.log
```

Treat `heun_final_nfe35.log` as the local source of truth.

### Step 4

Run the frozen reference baselines on the frontier proxy split if they are not already logged on this branch:

```bash
uv run run.py --sampler heun --split proxy > run_heun.log 2>&1
uv run run.py --sampler euler --split proxy > run_euler.log 2>&1
```

### Step 5

Run the current research sampler as-is on both scoreboards:

```bash
uv run run.py --sampler research --split proxy > run_research_frontier_proxy.log 2>&1
uv run run.py --sampler research --split proxy --nfe 35 > run_research_standard_proxy.log 2>&1
uv run run.py --sampler research --split confirm --nfe 35 > run_research_standard_confirm.log 2>&1
uv run run.py --sampler research --split final --nfe 35 > run_research_standard_final.log 2>&1
```

Extract the metrics:

```bash
grep "^start_time_utc:\|^end_time_utc:\|^nfe_.*runtime_s:\|^frontier_score:\|^fid_N\|^runtime_s:\|^peak_vram_mb:" run_research_frontier_proxy.log
grep "^start_time_utc:\|^end_time_utc:\|^nfe_.*runtime_s:\|^fid_N\|^runtime_s:\|^peak_vram_mb:" run_research_standard_proxy.log
grep "^start_time_utc:\|^end_time_utc:\|^nfe_.*runtime_s:\|^fid_N\|^runtime_s:\|^peak_vram_mb:" run_research_standard_confirm.log
grep "^start_time_utc:\|^end_time_utc:\|^nfe_.*runtime_s:\|^fid_N\|^runtime_s:\|^peak_vram_mb:" run_research_standard_final.log
```

The unmodified `research` run is the baseline for the editable slot on both scoreboards.

---

## Search splits

Use these three splits:

### `proxy`

- 5,000 samples
- fast screen only
- never sufficient on its own for a branch advancement claim

### `confirm`

- 10,000 samples
- medium-cost translation check
- used whenever a proxy improvement is small, noisy, or frontier-only

### `final`

- 50,000 samples
- paper-quality numbers
- the only split that can crown a new standard benchmark champion

---

## Required evaluation ladder for every candidate

For every candidate edit to `sample.py`, run the following ladder in order.
Do not skip the translation checks.

### Stage 1: frontier proxy

```bash
uv run run.py --sampler research --split proxy > run_frontier_proxy.log 2>&1
```

Read out:

```bash
grep "^start_time_utc:\|^end_time_utc:\|^nfe_.*runtime_s:\|^frontier_score:\|^fid_N\|^runtime_s:\|^peak_vram_mb:" run_frontier_proxy.log
```

### Stage 2: standard proxy translation check

```bash
uv run run.py --sampler research --split proxy --nfe 35 > run_standard_proxy.log 2>&1
```

Read out:

```bash
grep "^start_time_utc:\|^end_time_utc:\|^nfe_.*runtime_s:\|^fid_N\|^runtime_s:\|^peak_vram_mb:" run_standard_proxy.log
```

### Stage 3: confirm only if Stage 1 or Stage 2 looks promising

```bash
uv run run.py --sampler research --split confirm > run_frontier_confirm.log 2>&1
uv run run.py --sampler research --split confirm --nfe 35 > run_standard_confirm.log 2>&1
```

Read out:

```bash
grep "^start_time_utc:\|^end_time_utc:\|^nfe_.*runtime_s:\|^frontier_score:\|^fid_N\|^runtime_s:\|^peak_vram_mb:" run_frontier_confirm.log
grep "^start_time_utc:\|^end_time_utc:\|^nfe_.*runtime_s:\|^fid_N\|^runtime_s:\|^peak_vram_mb:" run_standard_confirm.log
```

### Stage 4: final standard challenge when promoted

```bash
uv run run.py --sampler research --split final --nfe 35 > run_standard_final.log 2>&1
```

Read out:

```bash
grep "^start_time_utc:\|^end_time_utc:\|^nfe_.*runtime_s:\|^fid_N\|^runtime_s:\|^peak_vram_mb:" run_standard_final.log
```

Only Stage 4 can update the standard champion.

---

## Keep / discard rule (revised)

A change must satisfy **both** a frontier rule and a standard translation rule.

### Frontier rule

A change is frontier-promising only if all of the following hold on `proxy`:

1. `frontier_score` improves, and
2. no individual frontier NFE regresses by more than **3%**, and
3. the code remains reasonably simple.

### Standard translation rule

A frontier-promising change may be kept only if the paired `NFE=35` run also satisfies:

1. on `proxy`, the `NFE=35` FID does **not regress materially** versus the current `last_standard_keep`, and
2. on `confirm`, the `NFE=35` FID also does not regress materially, and
3. the gap to local Heun at `NFE=35` does not widen in a meaningful way.

Use these default tolerances:

- on `proxy`: treat worse than **+1.0%** at `NFE=35` as a regression
- on `confirm`: treat worse than **+0.5%** at `NFE=35` as a regression
- on `final`: any clear worsening at `NFE=35` means the candidate is not a champion

### Important interpretation

- frontier win + standard regression = **discard**
- frontier win + standard neutral = **provisional only**, requires confirm
- frontier win + standard improvement = **promote** to final challenge
- standard improvement without frontier improvement can still be valuable if the mechanism is explicitly aimed at the standard benchmark

### Champion rule

A new branch champion must satisfy all of the following:

1. improve `FID@50K` at `NFE=35` versus the current `last_standard_keep`, and
2. reduce or preserve the gap versus local Heun, and
3. not regress any frontier NFE by more than **3%** on `final` if a frontier final is run, and
4. remain reasonably simple.

If a candidate improves frontier but fails this champion rule, it is not the new base commit.

---

## Main loop

LOOP FOREVER:

1. Look at the current git state.
2. Record the current `last_standard_keep`.
3. Propose **one concrete mechanism idea**.
4. Label it in your own notes as one of:
   - `mechanism`
   - `tuning`
5. Also label the target track:
   - `frontier`
   - `standard`
   - `both`
6. Edit only `sample.py`.
7. Commit the change.
8. Run the frontier proxy evaluation.
9. Run the paired standard proxy translation check at `NFE=35`.
10. If either run crashes, inspect the logs.
11. If frontier does not improve and standard does not improve, discard.
12. If frontier improves but standard proxy regresses materially, discard and reset to `last_standard_keep`.
13. If frontier improves and standard proxy is neutral or better, run `confirm` on both tracks.
14. Apply the revised keep/discard rule.
15. Only if the candidate passes the standard translation rule may it become the new working base.
16. After at most **3 promoted keeps** without a standard final challenge, run `final --nfe 35` before continuing.
17. If the final standard challenge fails, reset to `last_standard_keep`.
18. If it succeeds, advance `last_standard_keep`.
19. Log the result.

---

## Crash policy

If a run crashes:

1. inspect the last 50 log lines,
2. decide whether the crash is a trivial bug or a bad idea,
3. if trivial, fix and rerun,
4. if the idea is fundamentally unstable, mark it as `crash`, log it, revert to `last_standard_keep`, and move on.

Use:

- `0.000000` for `frontier_score`
- `0.0` for all FIDs
- `0.0` for VRAM

in crash rows.

Do not get stuck retrying the same broken idea forever.

---

## Logging results

Continue to use `results.tsv` for frontier bundle rows with the existing schema:

```text
commit	sampler	split	frontier_score	fid_N5	fid_N9	fid_N11	fid_N13	peak_vram_mb	status	notes
```

Rules:

- one row per frontier evaluation bundle,
- use `research` as the sampler name for the editable method,
- use `keep`, `discard`, or `crash`,
- keep notes short and concrete,
- include the mechanism family and whether the row was `mechanism` or `tuning`,
- do not commit `results.tsv` unless the human explicitly wants that.

### New required sidecar log for the standard benchmark

Also maintain a plain TSV file named `standard.tsv` with this schema:

```text
commit	sampler	split	nfe	fid	ref_heun_fid	gap_vs_heun	status	notes
```

Example:

```text
b91fc7c	research	final	35	2.2485	2.0073	0.2412	discard	frontier-only gain failed standard benchmark
```

Rules:

- one row per `NFE=35` evaluation,
- `ref_heun_fid` must come from the matching local Heun run on the same split tier,
- `gap_vs_heun = fid - ref_heun_fid`,
- negative is good,
- do not call a result a win unless the `gap_vs_heun` improves or stays safely neutral.

### Required timing fields in eval logs

Every long-running evaluation log must expose timing fields immediately, not only at process exit.

For `run.py` logs, require:

- `start_time_utc`
- `end_time_utc`
- `runtime_s`
- `nfe_<budget>_start_time_utc`
- `nfe_<budget>_progress`
- `nfe_<budget>_end_time_utc`
- `nfe_<budget>_runtime_s`

For `paper_eval.py` logs, require:

- `start_time_utc`
- `end_time_utc`
- `runtime_s`
- `block_<index>_start_time_utc`
- `block_<index>_generate_runtime_s`
- `block_<index>_fid_runtime_s`
- `block_<index>_end_time_utc`
- `block_<index>_runtime_s`

If a run looks slow, inspect these timing fields before deciding it is hung.

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
- step-size damping,
- monotone correction rules,
- simplified schedule or correction ideas grounded in the tracked EDM literature.

Especially good are ideas that:

- explain *why* a region of the trajectory is hard,
- predict whether the effect should help `NFE={5,9,11,13}`, `NFE=35`, or both,
- change *where* solver effort is spent,
- reduce error accumulation without touching model weights,
- and survive the standard translation gate.

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
- comparing only preview images and ignoring metrics,
- keeping frontier-only wins that fail the standard benchmark,
- more than 2 consecutive scalar-only same-family keeps,
- or treating a `proxy` result as if it were a final apples-to-apples result.

---

## Periodic validation cadence

### Every candidate that passes frontier proxy

Also run:

```bash
uv run run.py --sampler research --split proxy --nfe 35 > run_standard_proxy.log 2>&1
```

### Every candidate that passes frontier confirm

Also run:

```bash
uv run run.py --sampler research --split confirm --nfe 35 > run_standard_confirm.log 2>&1
```

### At most every 3 promoted keeps

Run the standard final challenge:

```bash
uv run run.py --sampler research --split final --nfe 35 > run_standard_final.log 2>&1
```

### Every 5 standard-qualified keeps

Run the frontier paper-quality sanity check:

```bash
uv run run.py --sampler research --split final --nfe 5,9 > run_final_short.log 2>&1
```

### Every 10 standard-qualified keeps

Run the full frontier final:

```bash
uv run run.py --sampler research --split final --nfe 5,9,11,13 > run_final_full.log 2>&1
```

### Every 5 standard-qualified keeps also export diagnostics

Export trajectory diagnostics for the current `research` sampler at:

- `NFE=11`
- `split=proxy`
- fixed diagnostic seeds

These are not the primary metric, but they help explain whether the mechanism is real.

---

## What counts as a good research idea

A good idea has all or most of these properties:

- it is visible in `sample.py`,
- it is explainable in one sentence,
- it changes the trajectory rather than the model,
- it can be ablated,
- it can be expressed as a small local change,
- it has a plausible mechanism,
- it predicts its own NFE signature,
- and it does not rely on proxy-only success.

Before each serious candidate, write down in your own notes:

- the mechanism family,
- the claimed failure region,
- whether the idea should help frontier, standard, or both,
- and what result would falsify the idea.

If you cannot say that clearly, the idea is probably not ready.

---

## Final interpretation rule

Use this exact language discipline:

- If a change improves only the frontier scoreboard, call it a **frontier-specific improvement**.
- If a change improves the standard scoreboard at `NFE=35`, call it a **standard benchmark improvement**.
- Only if it beats the local Heun comparator on `final`, `NFE=35`, may you call it a **better apples-to-apples result**.

Do not blur these categories.
