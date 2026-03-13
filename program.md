# sampler-autoresearch

## program.md

This repo is an experiment in autonomous sampler research on a **fixed pre-trained diffusion model**.

The repo is already set up. Your job is **not** to build infrastructure, redesign evaluation, or retrain a model. Your job is to improve the **sampling trajectory** by editing **one file only**:

- `sample.py`

Everything else is frozen unless a human explicitly changes the substrate.

---

## 0. Mission

The goal is **not** “get one more proxy win.”
The goal is to discover a sampler mechanism that survives three levels of scrutiny:

1. **cheap local frontier screening**,
2. **local `NFE=35` translation evidence**, and
3. **authoritative paper-path evaluation**.

The final aspiration is a result that is strong enough to defend and simple enough to explain.

You are doing **sampler mechanism research**, not benchmark gardening.

---

## 1. Ground truth about this repo

Treat the repo as having **three evaluation layers**.

### A. Auxiliary local frontier loop

This layer is the fast exploration loop:

- `run.py`
- `evaluate.py`
- `results.tsv`

This loop is designed around the frontier NFE set:

- `NFE = {5, 9, 11, 13}`
- `frontier_score` is computed from those frontier NFEs only
- split sizes are `proxy=5K`, `confirm=10K`, `final=50K`

Use this loop for fast search, family ranking, and failure diagnosis.

### B. Local standard translation layer

This layer is the local apples-to-apples translation check:

- `NFE = 35`
- this corresponds to the canonical **18-step EDM Heun regime**
- `standard.tsv` is the sidecar ledger for the local `NFE=35` result

**Important implementation detail:**
Do **not** assume that the correct local standard command is `run.py --nfe 35` by itself.
In this repo, the safe local bundle command is:

- `--nfe 5,9,11,13,35`

That bundle preserves the frontier calculation while also printing `fid_N35` to the log. The `fid_N35` value must then be copied into `standard.tsv`.

### C. Authoritative paper path

This is the claim path:

- `paper_eval.py`
- `paper_generate.py`
- upstream EDM `fid.py`
- `paper_results.tsv`

This is the source of truth for serious claims.
If the local loop and the paper path disagree, trust the paper path.

### Consequence

- `results.tsv` is the **exploration ledger**.
- `standard.tsv` is the **local translation ledger**.
- `paper_results.tsv` is the **claim ledger**.
- `experiment_reports.tsv` is the **periodic narrative ledger**.

Do **not** hard-code stale commit IDs or stale FID numbers in this file.
Always derive the current champions from the ledgers that exist in the current checkout.

---

## 2. Research target

The target is **unconditional CIFAR-10 on the official EDM paper path**.

Default authoritative comparison:

- target: `uncond`
- steps: `18`
- comparator: `paper_eval.py --sampler heun --target uncond --steps 18`
- research slot: `paper_eval.py --sampler research --target uncond --steps 18`

A result is not poster-level merely because it wins on proxy.
A result becomes a serious poster candidate only after it clears the paper path.

---

## 3. What counts as success

There are several success labels. Keep them separate.

### 1) Frontier improvement

A change improves the local frontier loop.
That means it helps the cheap search metric.
This is useful, but it is **not** a paper claim.

### 2) Local translation improvement

A change improves the local `fid_N35` result relative to the local Heun comparator and/or the best current research local standard result.
This is stronger than a frontier win, but it is still **not** authoritative.

### 3) Paper-side outcomes

Paper-side work has two stages of classification:

- block-0 screen: `screen_fail` or `paper_screen_pass`
- full paper run after a screen pass: `paper_loss`, `paper_micro_win`, or `paper_meaningful_win`

A block-0 improvement is not yet a paper win grade.
It is only a `paper_screen_pass` if it beats the current paper screen and earns a full paper run.

### Paper-side success labels

- `paper_screen_pass`: beats the current paper screen and earns a full paper run
- `paper_micro_win`: improves full paper metrics, but too small to change the Heun story
- `paper_meaningful_win`: improves full paper metrics enough to materially change the gap-to-Heun story
- `poster_candidate`: `paper_meaningful_win` vs Heun + coherent mechanism + ablation + simplicity

### 4) Poster candidate

You may call something a **poster candidate** only if all of the following hold:

1. it improves the authoritative paper-path result for `research`,
2. it matches or beats the best paper-path `heun` comparator for the same target and step count,
3. the change is explainable as **one coherent mechanism family**,
4. at least one ablation weakens or removes the effect,
5. the code remains simple enough to explain on one poster figure or in one paragraph,
6. the frontier loop does not show catastrophic collapse.

Until all of that is true, use weaker language:

- **frontier-specific improvement**
- **local translation improvement**
- **paper_screen_pass**
- **paper_micro_win**
- **paper_meaningful_win**

Only `paper_meaningful_win` may be described as real movement toward a poster candidate.
Do not blur these categories.

---

## 4. Start-of-run reading order

At the start of a fresh run, read these files in order:

1. `README.md`
2. `program.md`
3. `run.py`
4. `evaluate.py`
5. `sampler_protocol.py`
6. `paper_eval.py`
7. `paper_generate.py`
8. `sample.py`
9. `papers/manifest.yaml`
10. `results.tsv` if it exists
11. `standard.tsv` if it exists
12. `paper_results.tsv` if it exists

Also inspect recent git history or recent notes so that you do not repeat the same dead family blindly.

### Commit attribution discipline

Classify recent commits as one of:

- `research` = only `sample.py` changed
- `report` = only `experiment_reports.tsv` changed
- `meta` = logs / docs / ignore files / harness changes
- `human` = manual user commit

Only `research` commits count toward keeps, champions, and trial cadence.
Ignore `meta` and `human` commits when inferring the active mechanism family.

Do **not** reread the entire repo every iteration.
After the first pass, focus on:

- `sample.py`
- the active mechanism family
- the most recent kept and discarded commits
- the gap to local Heun at `NFE=35`
- the gap to paper-path Heun at `steps=18`

---

## 5. Frozen contract

### You may edit only

- `sample.py`

Inside `sample.py`, all of the following are fair game:

- schedule laws,
- sigma reparameterization,
- predictor-corrector structure,
- stateful correction rules,
- correction strength allocation,
- trajectory smoothing,
- local stabilizers,
- step-dependent gating,
- small scalar hyperparameters local to the sampler,
- simple mechanism-specific diagnostics returned through the existing trace machinery.

### You may not edit

Do **not** edit:

- `prepare.py`
- `run.py`
- `evaluate.py`
- `paper_eval.py`
- `paper_generate.py`
- `model_adapter.py`
- `sampler_protocol.py`
- anything in `samplers/`
- `pyproject.toml`
- the checkpoint
- the FID reference statistics
- the split sizes
- the frontier NFE set
- the paper target
- the paper step count for the canonical comparison

Do **not** add dependencies.
Do **not** retrain the diffusion model.
Do **not** add trainable sampler parameters.
Do **not** change seeds to cherry-pick wins.
Do **not** redefine the benchmark.

---

## 6. Do not hard-code moving baselines

This file must not embed fixed “current best” numbers that will go stale.

At the beginning of each session, derive these pointers from the ledgers:

- `frontier_heun_ref`: the best trustworthy local Heun frontier row
- `frontier_research_best`: the best trustworthy local research frontier row
- `standard_heun_ref`: the local Heun `final`, `NFE=35` row
- `standard_research_best`: the best trustworthy research `final`, `NFE=35` row
- `paper_heun_ref`: the best trustworthy paper-path Heun row for `target=uncond`, `steps=18`
- `paper_research_best`: the best trustworthy paper-path research row for `target=uncond`, `steps=18`

### Trustworthy means

- `status != crash`
- the row came from the correct target/split/step setting
- the notes are consistent with the mechanism family being tested
- the row was not later invalidated by a higher-tier failure

### Keep these commit pointers in notes

- `last_frontier_keep`
- `last_translation_keep`
- `last_paper_keep`
- `working_base`

Use this precedence:

1. if a paper-qualified best exists, `working_base = last_paper_keep`
2. else if a local final-qualified best exists, `working_base = last_translation_keep`
3. else `working_base = last_frontier_keep`

A frontier-only curiosity must **not** replace a stronger base commit.

---

## 7. Required hypothesis card for every serious candidate

Before each serious edit, write down a one-screen hypothesis card in your own notes.

Required fields:

- `family`
- `kind = mechanism | tuning`
- `track = frontier | standard | both`
- `base_commit`
- `hypothesis`
- `claimed_failure_region`
- `expected_signature`
- `ablation`
- `kill_condition`

### Example

```text
family=alpha_alignment_gate
kind=mechanism
track=standard
base_commit=<current working base>
hypothesis=late low-sigma steps are under-corrected in the 18-step regime, so alpha should increase only when adjacent slopes agree
claimed_failure_region=late standard regime, mostly neutral on frontier
expected_signature=fid_N35 improves; frontier largely flat; over-aggressive gate hurts confirm
ablation=replace gate with constant alpha or always-on alpha
kill_condition=confirm regresses or paper path stays flat
```

If you cannot explain the idea in this format, the idea is probably not ready.

---

## 8. Establish the evaluation substrate at the start of a run

### Step 1: confirm the git state

Record:

- current branch
- current commit
- uncommitted diff status

### Step 1.5: inspect GPU availability before expensive runs

Before launching any proposed sampling or paper-path run, inspect current GPU usage.

Minimum check:

```bash
nvidia-smi --query-gpu=index,name,memory.used,memory.total,utilization.gpu --format=csv,noheader
```

Rules:

- if an evaluation command already supports multi-GPU execution, use **all currently idle GPUs** for sampling instead of defaulting to a single GPU,
- prefer sharding the image generation workload across those idle GPUs,
- do **not** edit frozen infrastructure just to add parallelism where the current command path does not support it,
- if one backend fails on the available machine but another existing backend preserves the same sampling path, switch backends instead of falling back to single-GPU immediately,
- log the actual GPU count used for each authoritative run.

### Step 1.6: route redirected logs into `artifacts`

Set:

```bash
LOG_DIR=artifacts/logs
```

Rules:

- any shell-redirected stdout/stderr log (`> ... 2>&1`) must go under `artifacts/logs/` or a subdirectory of it,
- do **not** create new repo-root `*.log` files,
- prefer filenames that include the stage or commit when multiple candidates are active,
- keep these redirected logs untracked.

### Step 1.7: maintain periodic experiment reports

Keep a tracked TSV report ledger at:

- `experiment_reports.tsv`

Schema:

```text
report_utc	run_count_since_last_report	working_base	trials_done	performance_change	observations	next_action	commit_note
```

Rules:

- after every **5 completed evaluation runs**, append one detailed row,
- count local proxy/confirm/final bundles and paper promotions as runs for this cadence,
- if a paper promotion finishes before the 5-run boundary, append a report row immediately,
- `trials_done` must summarize the candidate commits and outcomes since the previous report,
- `performance_change` must record the observed metric deltas against the active local or paper references,
- `observations` must capture mechanistic or empirical takeaways, even for negative results,
- keep `experiment_reports.tsv` tracked in git and stage it into the next commit; if no code commit is imminent, make a dedicated notes commit so the report cadence is preserved.

### Step 2: ensure the ledgers exist or can be created

Required ledgers:

- `results.tsv`
- `standard.tsv`
- `paper_results.tsv`
- `experiment_reports.tsv`

`results.tsv` and `paper_results.tsv` have code-defined headers.
If `standard.tsv` does not exist, create it with the existing sidecar schema:

```text
commit	sampler	split	nfe	fid	ref_heun_fid	gap_vs_heun	status	notes
```

If `experiment_reports.tsv` does not exist, create it with this schema:

```text
report_utc	run_count_since_last_report	working_base	trials_done	performance_change	observations	next_action	commit_note
```

### Step 3: establish local Heun references if missing

Use the local bundle NFEs:

```bash
BUNDLE_NFES=5,9,11,13,35
```

Run:

```bash
uv run run.py --sampler heun --split proxy   --nfe ${BUNDLE_NFES} > ${LOG_DIR}/heun_proxy_bundle.log 2>&1
uv run run.py --sampler heun --split confirm --nfe ${BUNDLE_NFES} > ${LOG_DIR}/heun_confirm_bundle.log 2>&1
uv run run.py --sampler heun --split final   --nfe ${BUNDLE_NFES} > ${LOG_DIR}/heun_final_bundle.log 2>&1
```

Extract:

```bash
grep "^start_time_utc:\|^end_time_utc:\|^nfe_.*runtime_s:\|^frontier_score:\|^fid_N5:\|^fid_N9:\|^fid_N11:\|^fid_N13:\|^fid_N35:\|^runtime_s:\|^peak_vram_mb:" ${LOG_DIR}/heun_proxy_bundle.log
grep "^start_time_utc:\|^end_time_utc:\|^nfe_.*runtime_s:\|^frontier_score:\|^fid_N5:\|^fid_N9:\|^fid_N11:\|^fid_N13:\|^fid_N35:\|^runtime_s:\|^peak_vram_mb:" ${LOG_DIR}/heun_confirm_bundle.log
grep "^start_time_utc:\|^end_time_utc:\|^nfe_.*runtime_s:\|^frontier_score:\|^fid_N5:\|^fid_N9:\|^fid_N11:\|^fid_N13:\|^fid_N35:\|^runtime_s:\|^peak_vram_mb:" ${LOG_DIR}/heun_final_bundle.log
```

Append the `fid_N35` values to `standard.tsv` as the local Heun references.

### Step 4: establish the current research baseline if missing

Run:

```bash
uv run run.py --sampler research --split proxy   --nfe ${BUNDLE_NFES} > ${LOG_DIR}/research_proxy_bundle.log 2>&1
uv run run.py --sampler research --split confirm --nfe ${BUNDLE_NFES} > ${LOG_DIR}/research_confirm_bundle.log 2>&1
uv run run.py --sampler research --split final   --nfe ${BUNDLE_NFES} > ${LOG_DIR}/research_final_bundle.log 2>&1
```

Extract the same fields and append the `fid_N35` rows to `standard.tsv`.

### Step 5: establish the paper Heun comparator if missing

Run the authoritative comparator at least once:

```bash
uv run paper_eval.py --sampler heun --target uncond --steps 18 --gpus 1 > ${LOG_DIR}/paper_heun_uncond_steps18.log 2>&1
```

### Step 6: establish the current paper research baseline if missing

Run:

```bash
uv run paper_eval.py --sampler research --target uncond --steps 18 --gpus 1 > ${LOG_DIR}/paper_research_uncond_steps18.log 2>&1
```

Do **not** call a sampler a serious candidate if the paper comparator has never been established.

---

## 9. Scoreboards and which one matters

There are three scoreboards. They serve different purposes.

### Frontier scoreboard

- source: `results.tsv`
- metric: lower `frontier_score`
- purpose: cheap exploration only

### Local standard scoreboard

- source: `standard.tsv`
- metric: lower `fid` at `NFE=35`
- comparator: `ref_heun_fid`
- purpose: local translation evidence

### Paper scoreboard

- source: `paper_results.tsv`
- metric: lower `fid_min`
- comparator: paper-path Heun on the same target and step count
- purpose: authoritative claim

### Priority order

Use this priority order when making decisions:

1. **paper scoreboard** for claims and poster candidacy
2. **local standard scoreboard** for translation discipline
3. **frontier scoreboard** for cheap search

A frontier win that widens the higher-tier gap is not a real promotion.

---

## 10. Local bundle protocol

For the local loop, the default bundle is:

```bash
BUNDLE_NFES=5,9,11,13,35
```

Rationale:

- `frontier_score` still uses the frontier NFEs,
- `fid_N35` is printed in the same run,
- one bundle gives both exploration and translation evidence,
- `results.tsv` keeps its existing schema,
- `standard.tsv` can be maintained from the extracted `fid_N35` line.

### Rules for bundle use

- Use the bundle for `proxy`, `confirm`, and `final` local runs.
- Record the full frontier row in `results.tsv` through `run.py`.
- Record the `fid_N35` row in `standard.tsv` manually from the log.
- Do **not** pretend that `results.tsv` alone contains the local standard evidence.
- Before each bundle run, inspect GPU occupancy and place the run on an idle GPU instead of contending with active jobs.

---

## 11. Track-aware evaluation ladder

Every candidate must declare its intended track:

- `track=frontier`
- `track=standard`
- `track=both`
- `track=paper`

### A. `track=frontier`

This track is allowed to aim primarily at low NFE, but it still must obey translation discipline.

#### Stage F1: proxy bundle

```bash
uv run run.py --sampler research --split proxy --nfe ${BUNDLE_NFES} > ${LOG_DIR}/run_proxy_bundle.log 2>&1
```

#### Stage F2: confirm bundle if proxy is promising

```bash
uv run run.py --sampler research --split confirm --nfe ${BUNDLE_NFES} > ${LOG_DIR}/run_confirm_bundle.log 2>&1
```

#### Stage F3: final bundle if promoted

```bash
uv run run.py --sampler research --split final --nfe ${BUNDLE_NFES} > ${LOG_DIR}/run_final_bundle.log 2>&1
```

#### Stage F4: paper path for the best frontier family only

If a frontier family remains simple and survives the translation gate, run:

```bash
uv run paper_eval.py --sampler research --target uncond --steps 18 --gpus 1 > ${LOG_DIR}/paper_candidate.log 2>&1
```

### B. `track=standard`

This track is allowed to be neutral on frontier as long as it improves the `NFE=35` regime and does not break frontier badly.

#### Stage S1: proxy bundle

```bash
uv run run.py --sampler research --split proxy --nfe ${BUNDLE_NFES} > ${LOG_DIR}/run_proxy_bundle.log 2>&1
```

Judge primarily by `fid_N35`, secondarily by frontier sanity.

#### Stage S2: confirm bundle if proxy is promising

```bash
uv run run.py --sampler research --split confirm --nfe ${BUNDLE_NFES} > ${LOG_DIR}/run_confirm_bundle.log 2>&1
```

#### Stage S3: final bundle when promoted

```bash
uv run run.py --sampler research --split final --nfe ${BUNDLE_NFES} > ${LOG_DIR}/run_final_bundle.log 2>&1
```

#### Stage S4: authoritative paper promotion

A local standard winner should be promoted quickly to the paper path:

```bash
uv run paper_eval.py --sampler research --target uncond --steps 18 --gpus 1 > ${LOG_DIR}/paper_candidate.log 2>&1
```

### C. `track=both`

This track must satisfy both frontier and standard rules.
Use the same local bundle ladder, then promote to `paper_eval.py`.

### D. `track=paper`

Use this track when the active goal is to refine or ablate an already paper-promoted family.

- base = `last_paper_keep` if it exists, else `last_translation_keep`
- one candidate commit = one edit in `sample.py`, one hypothesis, one family

#### Stage P0: run a paper block-0 screen against the exact current paper screen reference

```bash
uv run paper_eval.py --sampler research --target uncond --steps 18 --repeats 1 --gpus 1 > ${LOG_DIR}/paper_block0_candidate.log 2>&1
```

Judge this run against the exact current paper screen reference for `seed_block_0`.

#### Stage P1: continue to full paper evaluation only if block 0 is strictly better

```bash
uv run paper_eval.py --sampler research --target uncond --steps 18 --gpus 1 > ${LOG_DIR}/paper_candidate.log 2>&1
```

#### Stage P2: classify the outcome as `paper_loss`, `paper_micro_win`, or `paper_meaningful_win`

Only `paper_meaningful_win` may be described as real movement toward a poster candidate.

---

## 12. Keep / discard rules

### Rule A: proxy is a screen, not a claim

A `proxy` improvement is permission to continue testing.
It is not enough to crown a champion.

### Rule B: every keep must name its tier

When you keep a candidate, label it explicitly as one of:

- `frontier_keep`
- `translation_keep`
- `paper_keep`

Do not use the word “champion” loosely.

### Rule C: track-aware decisions

#### For `track=frontier`

A candidate is allowed to be kept provisionally if:

1. `frontier_score` improves on `proxy`,
2. no individual frontier NFE regresses catastrophically,
3. `fid_N35` does not show clear local translation failure,
4. the code remains simple.

A frontier-only candidate cannot replace `working_base` unless it later survives a higher tier.

#### For `track=standard`

A candidate may be kept even if frontier is flat, provided that:

1. `fid_N35` improves on `proxy`,
2. the sign survives `confirm`,
3. `final` improves versus the current `last_translation_keep`,
4. frontier does not collapse.

For this track, **frontier flat is acceptable; frontier collapse is not**.

#### For `track=both`

A candidate must:

1. improve frontier meaningfully,
2. improve or safely preserve `fid_N35`,
3. remain simple.

#### For `track=paper`

Use this track only when iterating directly on an already paper-promoted family.

1. Stage P0 must beat the exact current paper screen reference on `seed_block_0`,
2. a `paper_screen_pass` is permission to continue, not a champion update by itself,
3. Stage P1 must be labeled `paper_loss`, `paper_micro_win`, or `paper_meaningful_win`,
4. only `paper_meaningful_win` may be described as real movement toward a poster candidate,
5. if the result is `paper_loss`, reset to the last stronger base.

### Rule D: higher-tier failure overrides lower-tier success

Use this precedence:

- paper failure overrides local success
- local final failure overrides proxy/confirm success
- confirm failure overrides proxy success

### Rule E: when in doubt, classify as neutral

Do **not** promote tiny one-off deltas aggressively.
If a result is so small that it is hard to distinguish from noise or extraction error, treat it as **neutral** until:

- the sign survives `confirm`, or
- the sign survives `final`, or
- the paper path preserves the sign.

### Rule F: simplicity matters

A tiny gain that turns `sample.py` into a tangled mess is usually not worth keeping.
A simpler mechanism with the same numbers is better research.

---

## 13. Champion rules

### Frontier champion

A frontier champion is the best currently trusted local low-NFE candidate.
It is useful for exploration, not for claims.

### Translation champion

A translation champion is the best currently trusted local `final`, `NFE=35` candidate in `standard.tsv`.
It is the default serious base for local iteration until the paper path says otherwise.

### Paper champion

A paper champion is the best currently trusted row in `paper_results.tsv` for:

- `sampler=research`
- `target=uncond`
- `steps=18`

If `paper_results.tsv` is not available in the visible checkout, reconstruct the current paper champion from the structured paper-side prefixes in `experiment_reports.tsv`.

Only the paper champion can anchor a poster-level claim.

### Promotion rule

A new `working_base` should usually come from the strongest available tier:

- prefer `paper_keep`
- otherwise prefer `translation_keep`
- otherwise keep `frontier_keep` only as a scouting branch, not as the main base

---

## 14. Promotion cadence to the paper path

### Story checkpoint before paper promotion

Before any paper-side promotion, write:

1. the signal being measured,
2. the trajectory region it is supposed to help,
3. one falsifiable prediction about what should move if the story is right.

If this cannot be written cleanly, do not promote the variant.

The paper path is expensive, so use it deliberately.
But do not postpone it forever.

Promote to `paper_eval.py` when any of the following is true:

1. a local `final`, `NFE=35` result becomes the new translation champion,
2. a new mechanism family survives `proxy` and `confirm` and remains explainable,
3. the branch has accumulated **3 local keeps** without a paper check,
4. the candidate is the first representative of a genuinely new family,
5. you believe the result is strong enough that you would mention it in a research note.

Do **not** let the search spend dozens of commits in local-only limbo.

---

## 15. Ablation rule

Every serious mechanism family must have an ablation.

At minimum, support one of these:

- turn the mechanism off,
- replace it with a constant version,
- move the gating region earlier or later,
- remove the stateful part while keeping the schedule,
- keep the same scalar budget but remove the logic.

Ablation is required before calling a paper-path win a poster candidate.

---

## 16. Anti-drift and plateau rules

These rules exist to prevent endless local hill-climbing without a story.

### Rule A: no frontier-only drift

A frontier keep that later fails local `final` or paper path must not become the new serious base.
Reset to the last stronger tier.

### Rule B: no endless same-family scalar twiddling

No more than **2 consecutive kept commits** may be scalar-only changes in the same family.
After that, the next serious iteration must do one of:

- switch family,
- add an ablation,
- simplify the mechanism,
- or promote the family to a higher tier.

### Rule C: no endless same-family paper micro-tuning

No more than 2 consecutive same-family `paper_micro_win` or `paper_screen_pass` commits may be kept.

After that, the next serious iteration must do one of:

- a simplifying ablation,
- a family switch,
- a new causal mechanism,
- or a full reset to the last stronger base.

### Rule D: retire a family after repeated higher-tier failure

Retire the family for the current run if any of the following happens:

- it produces **2 separate confirm regressions**,
- it produces **2 separate final regressions**,
- it reaches the paper path and fails clearly twice,
- it stays neutral for **3 serious attempts** with no clearer story.

### Rule E: no score hoarding

Do not keep stacking provisional keeps without promoting one representative to `final` or `paper_eval.py`.

---

## 17. Logging rules

### Redirected shell logs

Rules:

- all redirected stdout/stderr logs must live under `artifacts/logs/`,
- do **not** create new repo-root `*.log` files,
- prefer commit-scoped or stage-scoped filenames,
- treat these logs as disposable artifacts rather than tracked notes.

### `results.tsv`

`run.py` writes the frontier ledger with this schema:

```text
commit	sampler	split	frontier_score	fid_N5	fid_N9	fid_N11	fid_N13	peak_vram_mb	status	notes
```

Rules:

- one row per local frontier bundle run,
- use `research` as the sampler name for the editable slot,
- use `keep`, `discard`, or `crash`,
- keep notes short and concrete,
- prefix notes with `family=...; kind=...; track=...;` whenever possible,
- do not rewrite history,
- do not commit the file unless the human explicitly wants that.

### `standard.tsv`

Maintain the local translation sidecar with this schema:

```text
commit	sampler	split	nfe	fid	ref_heun_fid	gap_vs_heun	status	notes
```

Rules:

- one row per extracted local `fid_N35` result,
- `nfe` should be `35`,
- `ref_heun_fid` must come from the matching local Heun split,
- `gap_vs_heun = fid - ref_heun_fid`,
- negative is better,
- append only,
- do not invent rows that you did not actually run.

### `paper_results.tsv`

`paper_eval.py` writes the authoritative claim ledger.
Do not mutate its schema.
Use it exactly as produced by the code.
When the paper path uses multi-GPU generation, ensure the recorded GPU count reflects the actual launch width.

### `experiment_reports.tsv`

Maintain the tracked periodic report ledger with this schema:

```text
report_utc	run_count_since_last_report	working_base	trials_done	performance_change	observations	next_action	commit_note
```

### Paper-side reporting discipline

For any paper-side report row, begin the `trials_done` field with this structured prefix:

```text
paper_base=<sha>; candidate=<sha>; family=<name>; outcome=<screen_fail|paper_loss|paper_micro_win|paper_meaningful_win>; fid_blocks=<b0/b1/b2>; fid_min=<x>; heun_min=<y>; gap_to_heun=<z>;
```

If `paper_results.tsv` is not available in the visible checkout, this prefix must still be sufficient to reconstruct the current paper champion.

Rules:

- append one row every 5 completed evaluation runs, or sooner when a paper promotion finishes,
- for paper-side rows, keep the structured prefix first in `trials_done`, then summarize the candidate commits and outcomes since the previous report,
- describe the observed metric deltas versus the active local or paper references in `performance_change`,
- use `observations` for mechanistic takeaways, negative evidence, and stability notes,
- keep `next_action` concrete enough to guide the next experiment turn,
- keep this file tracked and periodically committed.

---

## 18. Crash policy

If a run crashes:

1. inspect the last 50 log lines under `artifacts/logs/`,
2. decide whether the crash is a trivial implementation bug or a bad idea,
3. if trivial, fix once and rerun,
4. if fundamentally unstable, mark it as `crash`, log it, revert to `working_base`, and move on.

Use the existing crash conventions for `results.tsv`.
For `standard.tsv`, record only real extracted `fid_N35` values from successful runs.
Do not get stuck retrying the same broken idea forever.

---

## 19. Main loop

LOOP FOREVER:

1. check git state,
2. identify `working_base`,
3. inspect recent keeps/discards so you do not repeat a dead family,
4. write one hypothesis card,
5. declare `track=frontier`, `track=standard`, `track=both`, or `track=paper`,
6. edit only `sample.py`,
7. commit the change,
8. if `track=paper`, run Stage P0 against the exact current paper screen reference,
9. if `track=paper` and block 0 fails, classify it as `screen_fail`, log it, reset to `working_base`, and continue,
10. if `track` is not `paper`, run the local proxy bundle,
11. if `track` is not `paper`, decide whether the candidate is frontier-promising, standard-promising, both, or neither,
12. if `track` is not `paper` and the candidate is not promising, discard and reset to `working_base`,
13. if `track` is not `paper` and the candidate is promising, run the local confirm bundle,
14. if `track` is not `paper` and confirm fails, discard and reset to `working_base`,
15. if `track` is not `paper` and confirm passes, decide whether the candidate deserves a local `final`,
16. if `track` is not `paper` and local `final` fails, discard and reset,
17. if `track` is not `paper` and local `final` wins, update `last_translation_keep`,
18. promote serious winners or `paper_screen_pass` candidates to full `paper_eval.py` on a disciplined cadence,
19. if the full paper result improves, classify it as `paper_micro_win` or `paper_meaningful_win` and update `last_paper_keep` if it becomes the best trusted row,
20. if the full paper result is `paper_loss`, do not let the candidate replace a stronger base,
21. only describe real poster-candidate movement after a `paper_meaningful_win`,
22. log the result,
23. if the report cadence boundary is hit, append and commit `experiment_reports.tsv`,
24. retire dead families,
25. continue.

Never run multiple unrelated mechanism changes in a single candidate commit.
One idea per commit.

---

## 20. Allowed experiment families

Good families include:

- better effort allocation across the trajectory,
- sigma-space reparameterization,
- late-step correction scheduling,
- predictor strength scheduling,
- slope-aware or curvature-aware gating,
- local consistency tests between adjacent steps,
- state smoothing or damped state transport,
- error-proxy-guided correction,
- simple region-specific order behavior,
- monotone stabilizers,
- simplifications of a stronger family that preserve the effect.

Especially good ideas:

- explain *why* a specific region is hard,
- predict **which regime** should benefit,
- produce a recognizable frontier/standard signature,
- remain small enough to ablate cleanly.

---

## 21. Disallowed directions

Do **not** spend iterations on:

- blind hyperparameter fishing with no mechanism story,
- repo restructuring,
- new dependencies,
- training side models,
- changing the FID implementation,
- changing seeds to rescue a weak result,
- preview-image cherry-picking,
- frontier-only wins that fail higher-tier checks,
- more than 2 consecutive scalar-only same-family keeps,
- more than 2 consecutive same-family `paper_micro_win` or `paper_screen_pass` keeps,
- or paper-claim language without paper-path evidence.

---

## 22. Language discipline

Use these exact categories:

- **frontier-specific improvement** = better local frontier only
- **local translation improvement** = better local `NFE=35`
- **screen_fail** = paper block 0 did not beat the current paper screen reference
- **paper_loss** = full paper run did not improve the trusted paper base
- **paper_screen_pass** = beats the current paper screen and earns a full paper run
- **paper_micro_win** = improves full paper metrics, but too small to change the Heun story
- **paper_meaningful_win** = improves full paper metrics enough to materially change the gap-to-Heun story
- **poster_candidate** = `paper_meaningful_win` vs Heun + coherent mechanism + ablation + simplicity

Only `paper_meaningful_win` counts as real movement toward a poster candidate.

Do not say:

- “new SOTA”
- “paper-level result”
- “better sampler”

unless the paper path actually supports it.

---

## 23. Final philosophy

This repo is not a sampler zoo.
It is a **mechanism search loop with translation discipline**.

Prefer ideas that are:

- local,
- explainable,
- ablatable,
- cheap enough to re-run,
- aligned with the official claim path,
- and simple enough to survive explanation.

A cheap proxy win is nice.
A local `NFE=35` win is better.
A paper-path win with a clear mechanism is the real target.
