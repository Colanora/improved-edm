# sampler-autoresearch

## Mission
Discover a **simple, literature-grounded, training-free sampler mechanism** that beats Heun on the authoritative paper path for unconditional CIFAR-10:

```bash
uv run paper_eval.py --sampler research --target uncond --steps 18 --gpus 1
```

You are doing **sampler mechanism research**, not benchmark gardening. A proxy win matters only if it translates to `NFE=35`, and then survives the official paper path.

---

## Ground truth
The **current checkout** is the source of truth.

- If this file disagrees with the current code, trust the code.
- Do not use stale commands copied from old notes or old docs.
- Do not assume the current best commit, current best FID, or current active family from memory; derive them from the visible ledgers in the checkout.

---

## Frozen contract
You may edit **only**:

- `sample.py`

You may **not**:

- change `run.py`, `evaluate.py`, `paper_eval.py`, `paper_generate.py`, `sampler_protocol.py`, or benchmark plumbing,
- change checkpoints, FID refs, seeds, split sizes, the frontier NFE set, or the canonical paper target/step count,
- retrain the model,
- add dependencies,
- add trainable sampler parameters,
- redefine the benchmark.

This repo is for **inference-time sampler research on a fixed pretrained model**.

---

## Evaluation hierarchy
There are three evaluation layers. Use them in this priority order for decisions:

1. `paper_results.tsv` = authoritative claim path
2. `standard.tsv` = local translation evidence at `NFE=35`
3. `results.tsv` = cheap frontier search at `NFE={5,9,11,13}`

Rule:

- **paper > standard > frontier**

A frontier improvement that worsens the higher tiers is not a real promotion.

---

## Session bootstrap
At the start of every session:

1. Read `README.md`, `AGENTS.md`, `program.md`, `sample.py`, and `paper_eval.py`.
2. Read `results.tsv`, `standard.tsv`, `paper_results.tsv`, and `experiment_reports.tsv` if they exist.
3. Derive these references from the current checkout:
   - `frontier_heun_ref`
   - `frontier_research_best`
   - `standard_heun_ref`
   - `standard_research_best`
   - `paper_heun_ref`
   - `paper_research_best`
4. Set `working_base` using this precedence:
   - `paper_research_best`
   - else `standard_research_best`
   - else `frontier_research_best`
5. If the current `sample.py` does **not** match `working_base`, restore or reconstruct `working_base` before testing a new idea.
6. Inspect recent **research** commits and the latest report rows so you do not repeat a dead family.

A frontier-only curiosity must not replace a stronger translation or paper-qualified base.

---

## Mandatory external research stage
The agent must actively use web search for current sampler research.

Do a literature pass at the start of every session, and again whenever:

- the active family has **2 misses**,
- the active family has **2 paper_micro_wins** without closing the gap to Heun,
- or you switch to a new family.

For each literature pass:

1. Read **3 to 5** relevant external papers or high-quality public method docs.
2. Prefer sources from arXiv, OpenReview, NeurIPS/ICLR/ICML/CVPR proceedings, or official code repos.
3. Write a short research map with one row per candidate family:

```text
family | external_anchor | portability | extra_nfe | active_nf_range | expected_signature | reject_if
```

Rules:

- `external_anchor` must name a real external method or paper, not an internal nickname.
- `portability` must be one of:
  - `direct` = implementable in `sample.py` only
  - `partial` = possible, but requires approximations, offline stats, or awkward adaptation
  - `incompatible` = requires retraining, learned coefficients, extra models, or harness changes
- Prefer `direct` families.
- Prefer `extra_nfe = 0` families unless there is a very strong reason otherwise.

Do **not** rely only on repo-local paper notes or only on the active code family.

---

## Candidate card
Before every serious edit, write a one-screen candidate card.

Required fields:

```text
family=
kind=mechanism|tuning
external_anchor=
portability=direct|partial|incompatible
base_commit=
active_nf_range=
extra_nfe=
hypothesis=
expected_signature=
ablation=
kill_condition=
```

Rules:

- One candidate card = one idea.
- `family` must describe a mechanism family, not a commit hash.
- `kind=tuning` is allowed only if it is anchored to a live mechanism family.
- If you cannot explain the idea in this format, the idea is not ready.

---

## Activity-aware evaluation
Every candidate must declare where it is expected to act.

Examples:

- `active_nf_range=frontier`
- `active_nf_range=standard,paper`
- `active_nf_range=late 18-step regime`
- `active_nf_range=low-NFE only`

Rules:

- Frontier NFEs correspond to very small step counts.
- If a mechanism is expected to act mainly in the `NFE=35` / 18-step regime, frontier is only a **sanity check**, not the main keep/discard signal.
- Do **not** kill a standard/paper-targeted idea solely because frontier is flat when the mechanism is inactive there.
- Do kill any idea that causes catastrophic frontier collapse, instability, NaNs, or obvious regression in the target regime.

---

## Local evaluation protocol
The default local bundle is:

```bash
uv run run.py --sampler research --split {proxy|confirm|final} --nfe 5,9,11,13,35
```

Use that bundle to get both:

- frontier evidence from `results.tsv`, and
- local translation evidence from `fid_N35`, recorded into `standard.tsv`.

Local tier meanings:

- `proxy` = cheap screen
- `confirm` = second filter
- `final` = stronger local evidence

Rules:

- Treat `proxy` and `confirm` as screens, not claims.
- A local keep must say which tier it belongs to: `frontier_keep` or `translation_keep`.
- A new local champion must still be judged against the active Heun reference and the current `working_base`.

---

## Paper promotion policy
Promote a candidate to the paper path when **any** of the following is true:

- it becomes the new best trustworthy local `NFE=35` result,
- it is the first clean representative of a genuinely new family,
- it has accumulated **2 local keeps** without a paper check,
- it is explicitly targeted at the 18-step / `NFE=35` regime,
- or it is strong enough that you would mention it in a research note.

Use the canonical claim command:

```bash
uv run paper_eval.py --sampler research --target uncond --steps 18 --gpus 1
```

Rules:

- Do not use unsupported stale commands from older notes.
- If the current checkout restricts paper evaluation to the official protocol, obey that restriction.
- Paper-path output is the source of truth for serious claims.

Paper-side labels:

- `paper_loss`
- `paper_micro_win`
- `paper_meaningful_win`
- `poster_candidate`

Only `paper_meaningful_win` counts as real movement toward a poster candidate.

---

## Keep / discard rules
Use these rules strictly:

1. **One candidate commit = one hypothesis.**
2. Every keep must name its tier:
   - `frontier_keep`
   - `translation_keep`
   - `paper_keep`
3. A frontier-only win may not replace a stronger translation or paper base.
4. Never continue search from a weaker `HEAD` than `working_base`.
5. After **2 scalar-only tweaks** inside the same family, either:
   - run the planned ablation/simplification, or
   - rotate to a different family.
6. After **2 misses** in the same family, rotate unless the next step is a clearly justified ablation.
7. After **2 paper_micro_wins** in the same family, simplify or rotate. Do not keep stacking gates and knobs indefinitely.
8. If a family needs many unrelated patches to survive, that is evidence against the family.

---

## Priority family queue
Default queue unless evidence clearly says otherwise:

1. **UniPC-style zero-extra-NFE corrector family**
2. **DPM-Solver / DEIS style dedicated diffusion ODE solver family**
3. **timestep / schedule-law family**
4. **late-stage higher-order correction or solver switching**, but only if it can be expressed as one clean mechanism
5. **controlled stochastic restart**, only if NFE accounting remains explicit and fair

Avoid spending long runs on same-family scalar twiddling of:

- alpha lift,
- predictor onset,
- predictor floor/cap,
- late relax,
- similar gate-strength micro-knobs,

unless there is a **fresh external anchor** and a **new falsifiable mechanism story**.

---

## Ablation requirement
Every family that reaches the paper path must have at least one ablation.

Valid ablations include:

- turn the mechanism off,
- replace it with a constant version,
- move the active region earlier or later,
- remove the stateful part while keeping the schedule,
- keep the scalar budget but remove the logic.

If the ablation does not weaken the effect, the mechanism story is not yet strong enough.

---

## Reporting
Maintain `experiment_reports.tsv` as the narrative ledger.

Append a row:

- after every **5 completed evaluation runs**, or
- immediately after any paper-path run finishes.

Each report row must state:

- `working_base`
- candidate commit(s)
- family
- outcome tier
- metric deltas vs active references
- mechanistic takeaway
- concrete next action

The purpose of the report is to compress learning, not to merely log that a run happened.

---

## Poster rule
A result may be called a **poster candidate** only if all of the following hold:

1. it improves the authoritative paper-path result for `research`,
2. it matches or beats the best trustworthy paper-path Heun result for `target=uncond`, `steps=18`,
3. the effect is explained by **one coherent mechanism family**,
4. at least one ablation weakens or removes the effect,
5. the code remains simple enough to explain in one figure or one paragraph,
6. frontier and local `NFE=35` do not show catastrophic collapse.

Until then, use weaker labels precisely.

---

## Anti-patterns
Do **not**:

- confuse proxy wins with paper wins,
- keep editing on top of an unverified weaker base,
- stay trapped in one family because it is easy to tune,
- skip literature search and reinvent old sampler ideas blindly,
- claim poster-level progress without a paper-path win over Heun,
- bury the real idea under many unrelated stabilizers.

The goal is not to produce a complicated sampler.
The goal is to produce a **defensible, simple, externally grounded mechanism** that survives the official evaluation path.
