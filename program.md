# sampler-autoresearch

## Mission
Discover a **simple, literature-grounded, training-free sampler mechanism** — preferably a clean new idea synthesized for this repo rather than a verbatim transplant — that beats Heun on the authoritative paper path for unconditional CIFAR-10:

```bash
uv run paper_eval.py --sampler research --target uncond --steps 18 --gpus 1
```

You are doing **sampler mechanism research**, not benchmark gardening. A proxy win matters only if it translates to the full-step regime, and then survives the official paper path.

Literature is a tool for proposing better ideas in this repo, not the endpoint. You may reproduce an external method or run a literature baseline when it is useful, but only in service of learning, calibration, ablation, or the design of a stronger repo-suited idea.

---

## Ground truth
The **current checkout** is the source of truth.

- If this file disagrees with the current code, trust the code.
- Do not use stale commands copied from old notes or old docs.
- Do not assume the current best commit, current best FID, or current active family from memory; derive them from the visible ledgers in the checkout.
- If legacy ledgers or commands from an older 3-stage protocol still exist, read them only as history; follow the active protocol in this file.

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
There are two active evaluation layers. Use them in this priority order for decisions:

1. `paper_results.tsv` = authoritative **50k** claim path
2. `results.tsv` = cheap **5k** proxy path

Rule:

- **paper > proxy**

A proxy improvement that worsens the paper path is not a real promotion.

Rules:

- The active protocol uses **one low-step regime** and **one full-step regime** only.
- The active protocol uses **5k** samples for proxy evidence and **50k** samples for paper-level evidence.
- Do **not** spend runs on a 3-stage `proxy/confirm/final` ladder or repeated `3 x 50k` paper sweeps.
- If the current checkout still contains old ledgers such as `standard.tsv`, treat them as historical context, not the active decision layer.

---

## Session bootstrap
At the start of every session:

1. Read `README.md`, `AGENTS.md`, `program.md`, `sample.py`, and `paper_eval.py`.
2. Read `results.tsv`, `paper_results.tsv`, `experiment_reports.tsv`, and the literature workspace files if they exist.
3. Derive these references from the current checkout:
   - `proxy_heun_ref`
   - `proxy_research_best`
   - `paper_heun_ref`
   - `paper_research_best`
4. Set `working_base` using this precedence:
   - `paper_research_best`
   - else `proxy_research_best`
5. If the current `sample.py` does **not** match `working_base`, restore or reconstruct `working_base` before testing a new idea.
6. Inspect recent **research** commits and the latest report rows so you do not repeat a dead family.
7. Initialize or update the literature workspace:
   - `literature/pdfs/`
   - `literature/literature_report.md`
8. Complete a **session literature pass** and write the required full-text notes before any serious edit, candidate card, or evaluation run.

Rules:

- A proxy-only curiosity must not replace a paper-qualified base.
- A session literature pass is a **hard gate**: no edit to `sample.py`, no candidate card, and no evaluation run until it is done.

---

## Research loop
A research session follows this loop:

1. **Bootstrap and restore base.**
2. **Run a session literature pass** and update the literature workspace until at least one candidate family is literature-grounded and pseudocode-ready.
3. **Write one candidate card** for one hypothesis.
4. **Edit `sample.py`** to implement exactly that hypothesis.
5. **Run evaluation** in the 2-layer protocol:
   - a **5k proxy** check,
   - and a **50k paper** check whenever promotion is justified.
6. **Decide keep / discard / ablate / rotate** using the higher-tier evidence.
7. **Report what was learned**, including the literature takeaway that produced or rejected the idea.
8. Repeat from step 2 or step 3 as appropriate:
   - return to **step 2** when the family rotates, the current family has 2 misses, the current family has 2 `paper_micro_win` outcomes without closing the gap, or the literature notes are still incomplete,
   - otherwise continue from **step 3** with the current family.

Termination condition:

- Stop only when a result satisfies the **Poster rule**, or when the current family is rejected and a new literature pass is required.

Rules:

- The default micro-loop is **literature -> candidate -> edit -> evaluate -> decide -> report**.
- The agent must not collapse the loop into pure `edit -> run -> tweak -> run` behavior.
- The literature pass is not a box-checking ritual; it must feed the next concrete mechanism idea, reject boundary, baseline probe, or ablation.

---

## Literature workspace and full-text requirement
Maintain a local literature workspace inside the repo root:

```text
literature/
  pdfs/
  literature_report.md
```

Rules:

- Every primary external paper used to justify a candidate family must be downloaded as a **local PDF file** into `literature/pdfs/` before that family can proceed to a serious edit.
- The agent must read from the **full text** of the local PDF, not just the abstract, title, memory, or a short web summary.
- If a source does not have an accessible PDF, it may be used only as a secondary hint, not as the primary anchor for a serious candidate family.
- `literature/literature_report.md` is the authoritative literature ledger for the session. If it is missing or incomplete, the literature pass is incomplete.
- Each paper entry in `literature/literature_report.md` must include enough detail that another agent could reconstruct the sampler mechanism without reopening the paper.

Each paper entry must contain:

- `paper_id`
- `title`
- `authors`
- `venue_or_source`
- `year`
- `url`
- `pdf_path`
- `family`
- `why_relevant`
- `core_claim`
- `assumptions`
- `complete_sampling_pseudocode`
- `state_variables_and_history`
- `nfe_accounting`
- `portability=direct|partial|incompatible`
- `repo_transfer_hypothesis`
- `failure_or_reject_boundary`
- `citation_followups`
- `status=ready|uncertain|rejected`

Rules for `complete_sampling_pseudocode`:

- It must be a **complete, executable-level pseudocode summary** of the sampler logic from the paper, not a one-line slogan.
- It must include inputs, outputs, state/history variables, step loop order, any predictor/corrector or multistep structure, terminal handling, and where model evaluations occur.
- It must make NFE accounting explicit.
- If the paper does not provide literal pseudocode, reconstruct it from the full method section, equations, appendix, or official code, and note that it is reconstructed.
- If a critical detail is still unclear after reading the paper, appendix, and official code/docs, mark the entry `status=uncertain` and **do not proceed** using that paper as a primary anchor.

A literature pass is complete only when the workspace contains:

- the local PDFs,
- a filled `literature/literature_report.md`,
- and at least one `status=ready` source whose pseudocode and portability judgment are complete enough to support a candidate card.

---

## Mandatory external research stage
The agent must actively use web search for current sampler research. Repo-local notes, user-provided papers, provided links, citation chains, related-work sections, and model memory are seeds, not substitutes.

Do a literature pass at the start of every session, and again whenever:

- the active family has **2 misses**,
- the active family has **2 paper_micro_wins** without closing the gap to Heun,
- you switch to a new family,
- or the current literature notes are still marked `uncertain` for the active family.

For each literature pass:

1. Read **3 to 5** relevant external papers or high-quality public method docs.
2. Prefer **recent** sources, especially **2025-2026** papers, when searching for fresh ideas, modern variants, and follow-up mechanisms.
3. Still include older seminal papers when they define the family or are needed to reconstruct the mechanism correctly.
4. Prefer sources from arXiv, OpenReview, NeurIPS/ICLR/ICML/CVPR proceedings, or official code repos.
5. Do **not** limit the pass to methods, papers, or links already named in this repo, prompt, or old notes.
6. At least **2** sources in each pass must be independently discovered external sources that were **not** already listed in the repo or the immediate task prompt.
7. Download the primary paper PDFs into `literature/pdfs/` before using them as anchors.
8. Read the **full docs** and summarize them in `literature/literature_report.md`.
9. Extract the sampler's complete pseudocode and portability judgment for each primary source.
10. Follow promising leads from the paper's **citations, bibliography, appendix, or related work** when they help clarify mechanism details, reveal newer variants, or open a better synthesized idea.
11. When a paper looks especially relevant but underspecified, do at least **one deeper follow-up** through its citations, related work, or official code/docs before using it as the main anchor.

Rules:

- `external_anchor` must name a real external method or paper, not an internal nickname.
- `portability` must be one of:
  - `direct` = implementable in `sample.py` only
  - `partial` = possible, but requires approximations, offline stats, or awkward adaptation
  - `incompatible` = requires retraining, learned coefficients, extra models, or harness changes
- Prefer `direct` families.
- Prefer `extra_nfe = 0` families unless there is a very strong reason otherwise.
- The literature pass is incomplete unless the literature workspace is written down **before** any serious edit or run.
- Internal memory of known methods does **not** satisfy this requirement; the pass must include session-fetched external sources.
- Recent papers are a **search preference**, not a ban on older anchors.

Do **not** rely only on repo-local paper notes or only on the active code family.

---

## Novelty and synthesis rule
Literature is a tool for generating new, simple, repo-suited ideas. It is **not** enough to cycle through named methods from papers and keep trying them one by one.

Rules:

- Each serious literature pass must produce at least **one synthesized candidate family**: a mechanism idea that is informed by external work but explicitly adapted, simplified, combined, or redirected for this fixed-pretrained, `sample.py`-only setting.
- Reproducing an external method or running a literature baseline is allowed only as a **calibration probe**, **translation probe**, **baseline comparison**, or **ablation scaffold**.
- If you run a near-direct reproduction or literature baseline, you must state what it is teaching you and what new mechanism idea, reject boundary, or ablation it enables next.
- A session is not successful if it only replays named literature methods without producing a sharper reject boundary, a portability lesson, a baseline calibration, or a new candidate mechanism.
- Prefer one clean synthesized idea over a long queue of superficial reproductions.

---

## Candidate card
Before every serious edit, write a one-screen candidate card.

Required fields:

```text
family=
kind=mechanism|tuning
external_anchor=
borrowed_mechanism=
synthesis_step=
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
- `external_anchor` must cite a real external method, paper, or public method doc whose full text has already been logged in the literature workspace.
- `borrowed_mechanism` must state what specific idea is being imported from the anchor.
- `synthesis_step` must state what is new, simplified, combined, or redirected for this repo relative to the anchor; if the candidate is a near-direct reproduction, write `none` and justify the probe value.
- If you cannot explain the idea in this format, the idea is not ready.

---

## Activity-aware evaluation
Every candidate must declare where it is expected to act.

Examples:

- `active_nf_range=proxy only`
- `active_nf_range=paper`
- `active_nf_range=late full-step regime`
- `active_nf_range=low-step only`
- `active_nf_range=both`

Rules:

- The active protocol uses **one low-step regime** and **one full-step regime** only.
- If a mechanism is expected to act mainly in the full-step regime, the low-step proxy is only a **sanity check**, not the main keep/discard signal.
- Do **not** kill a paper-targeted idea solely because the low-step proxy is flat when the mechanism is inactive there.
- Do kill any idea that causes catastrophic proxy collapse, instability, NaNs, or obvious regression in the target regime.

---

## Local evaluation protocol
The active evaluation protocol has only two stages:

- **proxy** = one low-step regime evaluated at **5k** samples
- **paper** = one full-step regime evaluated at **50k** samples through the authoritative path

Rules:

- Treat the **5k proxy** as a screen, not a claim.
- Treat the **50k paper** run as the authoritative claim path.
- Do **not** create a `proxy/confirm/final` ladder.
- Do **not** run repeated `3 x 50k` paper sweeps.
- A local keep must say whether it is a `proxy_keep` or `paper_keep`.
- A new local champion must still be judged against the active Heun reference and the current `working_base`.
- Use the current checkout's supported commands to realize the 5k proxy and the 50k paper run. Do not invent stale or unsupported commands.

---

## Paper promotion policy
Promote a candidate to the paper path when **any** of the following is true:

- it becomes the new best trustworthy proxy-to-paper translation candidate,
- it is the first clean representative of a genuinely new family,
- it has accumulated **2 proxy_keep** outcomes without a paper check,
- it is explicitly targeted at the full-step regime,
- it is a literature baseline or reproduction whose result is needed for calibration,
- or it is strong enough that you would mention it in a research note.

Use the canonical claim command:

```bash
uv run paper_eval.py --sampler research --target uncond --steps 18 --gpus 1
```

Rules:

- Do not use unsupported stale commands from older notes.
- If the current checkout restricts paper evaluation to the official protocol, obey that restriction.
- Paper-path output is the source of truth for serious claims.
- The active paper layer is **one 50k run**, not repeated `3 x 50k` sweeps.

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
   - `proxy_keep`
   - `paper_keep`
3. A proxy-only win may not replace a stronger paper base.
4. Never continue search from a weaker `HEAD` than `working_base`.
5. After **2 scalar-only tweaks** inside the same family, either:
   - run the planned ablation/simplification, or
   - rotate to a different family.
6. After **2 misses** in the same family, rotate unless the next step is a clearly justified ablation.
7. After **2 paper_micro_wins** in the same family, simplify or rotate. Do not keep stacking gates and knobs indefinitely.
8. If a family needs many unrelated patches to survive, that is evidence against the family.
9. After **2 reproduction/probe candidates** from literature without yielding a clear synthesized family, stop replaying names from the literature; write down a new mechanism idea or rotate.

---

## Priority family queue
Default queue unless evidence clearly says otherwise. This queue is a **search prior**, not a closed menu; literature may surface a better family and justify reordering it.

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

- after every **3 completed evaluation runs**, or
- immediately after any paper-path run finishes.

Each report row must state:

- `working_base`
- candidate commit(s)
- family
- outcome tier
- metric deltas vs active references
- mechanistic takeaway
- concrete next action

If a literature pass occurred since the last report, also state:

- the main `external_anchor` set consulted,
- the main `pdf_path` set added,
- the portability takeaway,
- the baseline or reproduction lesson if any,
- and the synthesized idea or reject boundary it produced.

The purpose of the report is to compress learning, not to merely log that a run happened.

---

## Poster rule
A result may be called a **poster candidate** only if all of the following hold:

1. it improves the authoritative paper-path result for `research`,
2. it matches or beats the best trustworthy paper-path Heun result for `target=uncond`, `steps=18`,
3. the effect is explained by **one coherent mechanism family**,
4. at least one ablation weakens or removes the effect,
5. the code remains simple enough to explain in one figure or one paragraph,
6. the 5k proxy and the 50k paper run do not show catastrophic collapse.

Until then, use weaker labels precisely.

---

## Anti-patterns
Do **not**:

- confuse proxy wins with paper wins,
- keep editing on top of an unverified weaker base,
- stay trapped in one family because it is easy to tune,
- skip literature search and reinvent old sampler ideas blindly,
- limit literature search to repo-provided or already-named methods,
- treat literature search as a box-checking ritual,
- read only abstracts or summaries when the method details matter,
- use a paper as a primary anchor without downloading and reading its PDF,
- proceed when the literature report still lacks correct sampler pseudocode,
- replay named methods from papers without extracting a repo-suited mechanism idea,
- waste budget on repeated `3 x 50k` sweeps,
- claim poster-level progress without a paper-path win over Heun,
- bury the real idea under many unrelated stabilizers.

The goal is not to produce a complicated sampler.
The goal is not to reproduce a literature survey inside `sample.py`.
The goal is to produce a **defensible, simple, externally grounded mechanism** that survives the official evaluation path.
