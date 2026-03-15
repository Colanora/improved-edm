# sampler-autoresearch

## Mission
Discover a **simple, literature-grounded, training-free sampler mechanism** — preferably a clean new idea synthesized for this repo rather than a verbatim transplant — that beats Heun on the authoritative paper path for unconditional CIFAR-10:

```bash
uv run paper_eval.py --sampler research --target uncond --steps 18 --gpus 1
```

You are doing **sampler mechanism research**, not benchmark gardening.

A proxy win matters only if it translates to the full-step regime, and then survives the official paper path. Literature is a tool for proposing better ideas in this repo, not the endpoint. You may reproduce an external method or run a literature baseline when it is useful, but only in service of learning, calibration, ablation, or the design of a stronger repo-suited idea.

Do **not** redefine progress as a same-family micro-tweak that only nicks a lucky scalar while weakening the mechanism story.

---

## Ground truth
The **current checkout** is the source of truth.

- If this file disagrees with the current code, trust the code.
- Do not use stale commands copied from old notes or old docs.
- Do not assume the current best commit, current best FID, or current active family from memory; derive them from the visible ledgers in the checkout.
- If legacy ledgers or commands from an older protocol still exist, read them only as history; follow the active protocol in this file.

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

1. `paper_results.tsv` = authoritative **paper** claim path as recorded by the current checkout's `paper_eval.py`
2. `results.tsv` = cheap **5k** proxy path

Rule:

- **paper > proxy**. A proxy improvement that worsens the paper path is not a real promotion.

Rules:

- The active protocol uses **one low-step regime** and **one full-step regime** only.
- The active protocol uses **5k** samples for proxy evidence.
- The active paper path is exactly what the current checkout's `paper_eval.py` records. In the current checkout, that is the official **3-block** paper protocol with **3 x 50k** seed blocks written as one row in `paper_results.tsv`.
- Do **not** spend runs on a legacy `proxy/confirm/final` ladder or invent unofficial paper shortcuts that disagree with the current checkout.
- If the current checkout still contains old ledgers such as `standard.tsv`, treat them as historical context, not the active decision layer.
- When comparing paper rows, use the **full seed-block vector** and the corresponding **paper mean** as the primary signal. Treat `fid_min` as a secondary note or tiebreaker, not as the incumbent selector by itself.
- `paper_mean` means the arithmetic mean of the recorded paper seed blocks for that row.

---

## Session bootstrap
At the start of every session:

1. Read `README.md`, `AGENTS.md`, `program.md`, `sample.py`, and `paper_eval.py`.
2. Read `results.tsv`, `paper_results.tsv`, `experiment_reports.tsv`, and the literature workspace if it exists. Start with `literature/literature_report.md`, then open the latest pass file and only the paper notes relevant to the active family.
3. Derive these references from the current checkout:
   - `proxy_heun_ref`
   - `proxy_research_best`
   - `paper_heun_ref`
   - `paper_research_best`
4. Derive `paper_heun_ref` and `paper_research_best` from **full paper rows**, not from a single lucky `fid_min`.
5. Prefer the row with the better overall seed-block vector / `paper_mean`; use `fid_min` only as a secondary tiebreaker.
6. If two paper rows are effectively tied, prefer the simpler and more ablatable mechanism family as `working_base`, not the noisier row with one lucky block.
7. Set `working_base` using this precedence:
   - `paper_research_best`
   - else `proxy_research_best`
8. If the current `sample.py` does **not** match `working_base`, restore or reconstruct `working_base` before testing a new idea.
9. Inspect recent **research** commits and the latest report rows so you do not repeat a dead family.
10. Initialize or update the literature workspace:
    - `literature/literature_report.md`
    - `literature/papers/`
    - `literature/passes/`
    - `literature/pdfs/`
11. Complete a **hard reflection pass** over the current literature workspace and recent evidence before any serious edit, candidate card, or evaluation run.

Rules:

- A proxy-only curiosity must not replace a paper-qualified base.
- A hard reflection pass is a **hard gate**: no edit to `sample.py`, no candidate card, and no evaluation run until it is done.
- A fresh discovery pass is **not** required at the start of every session. Reuse the existing literature workspace first, and read new papers only if reflection identifies a concrete unresolved question or no unused viable primary anchor remains.

---

## Research loop
A research session follows this loop:

1. **Bootstrap and restore base.**
2. **Run a hard reflection pass** on the current literature workspace, recent results, and the active family state.
3. If reflection returns `targeted_followup_required`, do a **targeted literature follow-up or discovery pass**, update the literature workspace, and return to **step 2**.
4. **Write one candidate card** for one hypothesis.
5. **Edit `sample.py`** to implement exactly that hypothesis.
6. **Run evaluation** in the 2-layer protocol:
   - a **5k proxy** check,
   - and a paper-path check whenever promotion is justified.
7. **Decide keep / discard / ablate / rotate** using the higher-tier evidence.
8. **Report what was learned**, including whether existing literature was sufficient or what exact gap forced new reading.
9. Repeat from **step 2** before the next serious experiment:
   - reflection is mandatory again when the family rotates, the current family has 2 misses, the current family has 2 `paper_micro_win` outcomes without closing the gap, the next move is an ablation or calibration probe, or the literature notes are still incomplete,
   - if reflection says the existing reviewed papers already cover the next move, continue without adding new papers,
   - if reflection says a gap remains, do only the narrow follow-up reading needed and then rerun reflection.

Termination condition:

- Stop only when a result satisfies the **Poster rule**, or when the current family is rejected and reflection concludes that a targeted follow-up literature pass is required before any further move.

Rules:

- The default micro-loop is **reflection -> candidate -> edit -> evaluate -> decide -> report**.
- The expanded loop is **reflection -> (targeted follow-up only if needed) -> candidate -> edit -> evaluate -> decide -> report**.
- The agent must not collapse the loop into pure `edit -> run -> tweak -> run` behavior or into endless `search -> read -> search -> read` behavior.
- After a long literature journey, hard reflection must explicitly choose the highest-value next move from the papers already reviewed. The paper pool is finite, and not every new search will yield a valuable paper.
- The reflection pass is not a box-checking ritual; it must feed the next concrete mechanism idea, reject boundary, baseline probe, ablation, or explicit decision that no new paper is needed this turn.
- Keep a 2-track cadence: **incumbent consolidation** (ablation or simplification of the best paper-supported family) and **orthogonal family exploration** (a genuinely different mechanism family). Do not stay indefinitely inside near-neighbor late-stage Heun variants.

---

## Hard reflection stage
Before any candidate card, serious edit, or evaluation, run a hard reflection pass over the current results and literature workspace.

Each reflection pass must produce:

- `pass_kind=reflection`
- `primary_anchor=` one reviewed paper that is still `primary_use=unused`, or `none` if the next move is a same-family ablation or calibration probe that does not need a new primary anchor
- `technical_check_refs=` reviewed papers reopened only to verify details, derivations, edge cases, appendix logic, code behavior, or citations
- `next_move=` one of `new_family|ablation|calibration_probe|reject_and_rotate`
- `highest_value_rationale=` why this is the single most valuable next move available from the literature already collected
- `reflection_verdict=existing_literature_sufficient|targeted_followup_required`
- `followup_question=` the exact unresolved technical question or missing family gap when `reflection_verdict=targeted_followup_required`

Rules:

- Treat the reviewed paper pool as finite. Do **not** keep expanding it by default.
- Every reviewed paper may be used only once as a new `primary_anchor` for a family line.
- A paper already marked `primary_use=used` may still be reopened in `technical_check_refs` whenever you want to be humble about the details and verify the technique more deeply.
- If an existing reviewed paper, appendix, citation trail, or official code/doc can answer the current question, revisit it instead of reading a new paper.
- Only when no existing reviewed source can answer the question, or no unused viable `primary_anchor` remains for the next move, may reflection escalate to targeted external discovery.
- If reflection yields `targeted_followup_required`, stop before the candidate card, serious edit, and evaluation. Do only the narrow follow-up reading needed, then rerun reflection.

---

## Literature workspace and full-text requirement
Maintain a local literature workspace inside the repo root:

```text
literature/
  literature_report.md
  papers/
  passes/
  pdfs/
```

Rules:

- Every primary external paper used to justify a candidate family must be downloaded as a **local PDF file** into `literature/pdfs/` before that family can proceed to a serious edit.
- The agent must read from the **full text** of the local PDF, not just the abstract, title, memory, or a short web summary.
- If a source does not have an accessible PDF, it may be used only as a secondary hint, not as the primary anchor for a serious candidate family.
- `literature/literature_report.md` is the authoritative top-level literature index and current-state ledger for the session. If it is missing or incomplete, the reflection pass is incomplete.
- Keep `literature/literature_report.md` compact: it should say the current working base, the latest reflection or follow-up pass, the current active or next candidate family, the current next action, whether existing literature is sufficient, and the paper/pass indexes.
- Each paper note in `literature/papers/<paper_id>.md` is the authoritative full-text note for that paper and must include enough detail that another agent could reconstruct the sampler mechanism without reopening the paper.
- Each pass file in `literature/passes/pass_XX.md` is the authoritative chronological synthesis record for a reflection pass, discovery pass, or follow-up check.
- Read the root report first, then the latest pass file, then only the paper notes you need.

Each paper note must contain:

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
- `primary_use=unused|used`
- `primary_use_family=none|<family>`
- `status=ready|uncertain|rejected`

Each pass file must contain:

- `pass_id`
- `pass_kind=reflection|discovery|followup_check`
- `session_date`
- `working_paper_base`
- `trigger`
- `paper_refs`
- `primary_anchor`
- `technical_check_refs`
- `new_paper_refs`
- `candidate_families`
- `reflection_verdict=existing_literature_sufficient|targeted_followup_required`
- `followup_question`
- the pass takeaway
- the candidate cards produced from that pass

Rules for `complete_sampling_pseudocode`:

- It must be a **complete, executable-level pseudocode summary** of the sampler logic from the paper, not a one-line slogan.
- It must include inputs, outputs, state/history variables, step loop order, any predictor/corrector or multistep structure, terminal handling, and where model evaluations occur.
- It must make NFE accounting explicit.
- If the paper does not provide literal pseudocode, reconstruct it from the full method section, equations, appendix, or official code, and note that it is reconstructed.
- If a critical detail is still unclear after reading the paper, appendix, and official code/docs, mark the entry `status=uncertain` and **do not proceed** using that paper as a primary anchor.

A paper's one primary use belongs to the family named in `primary_use_family`.

Rules:

- Same-family ablations, simplifications, and calibration probes may keep citing that family's original `external_anchor`, but this does **not** create a new primary use.
- A paper already assigned to one family line may not later be reintroduced as a fresh `primary_anchor` for a different family.

A reflection/discovery cycle is recorded completely only when the workspace contains:

- the local PDFs,
- a filled `literature/literature_report.md`,
- the current `literature/passes/pass_XX.md`,
- and either:
  - at least one `status=ready` paper note whose pseudocode, portability judgment, and `primary_use` state are complete enough to support the selected `primary_anchor`,
  - or an explicit `followup_question` explaining why no serious edit or run may proceed yet.

---

## Targeted external research stage
The agent must actively use web search for current sampler research when hard reflection identifies a real gap. Repo-local notes, user-provided papers, provided links, citation chains, related-work sections, and model memory are seeds, not substitutes once a missing detail or missing family has been identified.

Run targeted external discovery or follow-up only when:

- hard reflection returns `targeted_followup_required`,
- no unused viable `primary_anchor` remains for the next move,
- a critical technical detail remains unresolved after reopening the relevant reviewed papers or notes,
- you switch to a new family and the current workspace has no ready unused anchor for that family,
- or the current literature notes are still marked `uncertain` for the active family after exhausting the existing reviewed sources.

For each targeted discovery or follow-up pass:

1. Write the exact `followup_question` or missing-family gap before searching for anything new.
2. Reopen the relevant reviewed paper notes, local PDFs, appendix sections, citation trails, and official code/docs first.
3. Only if the gap remains unresolved, read the smallest new external set needed to close it, usually **1 to 2** papers or high-quality public method docs and at most **3**.
4. Prefer **recent** sources, especially **2025-2026** papers, when searching for fresh ideas, modern variants, and follow-up mechanisms.
5. Still include older seminal papers when they define the family or are needed to reconstruct the mechanism correctly.
6. Prefer sources from arXiv, OpenReview, NeurIPS/ICLR/ICML/CVPR proceedings, or official code repos.
7. Do **not** read new papers just to satisfy ritual, quota, or session freshness.
8. Download the primary paper PDFs into `literature/pdfs/` before using them as anchors.
9. Read the **full docs** and summarize them in the corresponding paper notes under `literature/papers/`.
10. Extract the sampler's complete pseudocode, portability judgment, and `primary_use` state for each primary source, and update the current `literature/passes/pass_XX.md` with the takeaway, reject boundary, and candidate cards produced by the pass.
11. Follow promising leads from the paper's **citations, bibliography, appendix, or related work** when they help clarify mechanism details, reveal newer variants, or answer the exact follow-up question.
12. When a paper looks especially relevant but underspecified, do at least **one deeper follow-up** through its citations, related work, or official code/docs before using it as the main anchor.
13. After any new reading, rerun hard reflection and explicitly decide whether the existing literature is now sufficient.

Rules:

- `external_anchor` must name a real external method or paper, not an internal nickname.
- `portability` must be one of:
  - `direct` = implementable in `sample.py` only
  - `partial` = possible, but requires approximations, offline stats, or awkward adaptation
  - `incompatible` = requires retraining, learned coefficients, extra models, or harness changes
- Prefer `direct` families for mainline implementation.
- Prefer `extra_nfe = 0` families unless there is a very strong reason otherwise.
- When a strong paper is judged `partial` or `incompatible`, write the exact blocker in the relevant `literature/papers/<paper_id>.md` and mention it in the current `literature/passes/pass_XX.md`. Do **not** silently compress it into a nearby Heun patch and call that a faithful probe.
- A targeted discovery pass is incomplete unless the literature workspace is written down **before** any serious edit or run that depends on it.
- Internal memory of known methods does **not** satisfy this requirement when reflection has already determined that external follow-up is needed.
- Recent papers are a **search preference**, not a ban on older anchors. Do **not** rely only on repo-local paper notes or only on the active code family.
- A previously used `primary_anchor` may still appear in `technical_check_refs`, but it may not be recycled as the next new family's primary source.

---

## Novelty and synthesis rule
Literature is a tool for generating new, simple, repo-suited ideas. It is **not** enough to cycle through named methods from papers and keep trying them one by one.

Rules:

- Each serious reflection cycle must produce at least one of:
  - a synthesized candidate family,
  - a justified same-family ablation or calibration probe,
  - or a sharper reject boundary that explains why targeted follow-up or rotation is needed next.
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
technical_check_refs=
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
- `external_anchor` must cite the single real external method, paper, or public method doc whose full text has already been logged in the literature workspace and whose family line owns the candidate.
- `technical_check_refs` lists previously reviewed papers or docs reopened only for detail verification; write `none` when there are no supporting detail checks.
- `external_anchor` may remain the same for later same-family ablations or calibration probes, but it may not be reassigned as a fresh primary anchor for a different family.
- `borrowed_mechanism` must state what specific idea is being imported from the anchor.
- Supporting detail checks may clarify the implementation, but they may not replace the `external_anchor` as the main source of the idea.
- `synthesis_step` must state what is new, simplified, combined, or redirected for this repo relative to the anchor; if the candidate is a near-direct reproduction, write `none` and justify the probe value.
- If the candidate claims to be a new family, it must state what makes it mechanistically different from the current `working_base`; window changes, gate shifts, or coefficient twiddles alone do not qualify.
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
- Mild proxy loss by itself is **not** a veto for an explicitly paper-targeted idea if the mechanism is inactive in proxy and there is no instability or obvious target-regime regression.
- Do kill any idea that causes catastrophic proxy collapse, instability, NaNs, or obvious regression in the target regime.

---

## Local evaluation protocol
The active evaluation protocol has only two stages:

- **proxy** = one low-step regime evaluated at **5k** samples
- **paper** = one full-step regime evaluated through the authoritative path recorded by the current checkout's `paper_eval.py`

Rules:

- Treat the **5k proxy** as a screen, not a claim.
- Treat the paper run recorded by `paper_eval.py` as the authoritative claim path.
- Do **not** create a `proxy/confirm/final` ladder.
- Do **not** invent unofficial single-block paper shortcuts.
- A local keep must say whether it is a `proxy_keep` or `paper_keep`.
- A new local champion must still be judged against the active Heun reference and the current `working_base`.
- When reading `paper_results.tsv`, compare the full seed-block vector and `paper_mean` before looking at `fid_min`.
- Use the maximum currently idle visible GPUs for every evaluation run; proxy eval should shard the single 5k seed set across GPUs rather than adding extra seed blocks.
- Use the current checkout's supported commands to realize the 5k proxy and the paper-path run. Do not invent stale or unsupported commands.

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

Execution note:

- use all idle gpus for generation and fid calculation(if we can)
- use nccl backend(we have 32g shm)

Rules:

- Do not use unsupported stale commands from older notes.
- If the current checkout restricts paper evaluation to the official protocol, obey that restriction.
- Paper-path output is the source of truth for serious claims.
- The active paper layer is the current checkout's official `paper_eval.py` path. In this checkout, that means one recorded paper-evaluation row containing **3 x 50k** seed blocks.
- Assign paper-side labels from the **full paper row**. A lucky `fid_min` without supportive block-vector / `paper_mean` evidence is not enough for `paper_keep`.

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
4. A paper keep or new incumbent must be supported by the full paper row, not only by a lone `fid_min` dip.
5. Never continue search from a weaker `HEAD` than `working_base`.
6. After **2 scalar-only tweaks** inside the same family, either:
   - run the planned ablation/simplification, or
   - rotate to a genuinely orthogonal family.
7. After **2 misses** in the same family, rotate unless the next step is a clearly justified ablation.
8. After **2 paper_micro_wins** in the same family, simplify or rotate. Do not keep stacking gates and knobs indefinitely.
9. If a family needs many unrelated patches to survive, that is evidence against the family.
10. After **2 reproduction/probe candidates** from literature without yielding a clear synthesized family, stop replaying names from the literature; write down a new mechanism idea or rotate.
11. A "new family" must be mechanistically different from the active one; changing only windows, gates, relax weights, predictor constants, or similar micro-knobs does not count as a family rotation.

---

## Priority family queue
Default queue unless evidence clearly says otherwise. This queue is a **search prior**, not a closed menu; literature may surface a better family and justify reordering it.

- If the active family already has a credible `paper_keep`, the next non-ablation paper probe should prefer a genuinely orthogonal family from this queue rather than another near-neighbor patch.

1. **UniPC-style zero-extra-NFE corrector family**
2. **DPM-Solver / DEIS style dedicated diffusion ODE solver family**
3. **timestep / schedule-law family**
4. **late-stage higher-order correction or solver switching**, but only if it can be expressed as one clean mechanism
5. **controlled stochastic restart**, only if NFE accounting remains explicit and fair

- If literature points to a strong `partial` family outside this queue, run at least one explicit portability probe or write a reject boundary. Do not ignore strong families silently just because they are awkward under the frozen contract.

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
- paper block vector / `paper_mean` when paper data exists
- mechanistic takeaway
- concrete next action

If a reflection pass or targeted discovery pass occurred since the last report, also state:

- whether the turn was `reflection_only` or `new_literature_added`,
- why no new paper was needed, or the exact `followup_question` that forced new reading,
- the main `external_anchor` and `technical_check_refs` consulted,
- the main `pdf_path` set added, if any,
- the portability takeaway,
- the baseline or reproduction lesson if any,
- and the synthesized idea or reject boundary it produced.

The purpose of the report is to compress learning, not to merely log that a run happened.

---

## Poster rule
A result may be called a **poster candidate** only if all of the following hold:

1. it improves the authoritative paper-path result for `research` on the **full paper row**, not only on a lucky `fid_min`,
2. it matches or beats the best trustworthy paper-path Heun result for `target=uncond`, `steps=18` on the **full paper row**,
3. the effect is explained by **one coherent mechanism family**,
4. at least one ablation weakens or removes the effect,
5. the code remains simple enough to explain in one figure or one paragraph,
6. the 5k proxy and the authoritative paper path do not show catastrophic collapse.

Until then, use weaker labels precisely.

---

## Anti-patterns
Do **not**:

- confuse proxy wins with paper wins,
- keep editing on top of an unverified weaker base,
- select incumbents by a single lucky `fid_min` while ignoring the rest of the paper row,
- rename near-neighbor gate/window/constant tweaks as a new family,
- skip hard reflection and jump from accumulated reading straight into experiments,
- assume every session or every miss requires a fresh broad literature sweep,
- keep adding papers when the current reviewed set already answers the real technical question,
- reuse a previously consumed primary anchor as if it were a brand-new family source,
- silently compress a `partial` literature method into a nearby Heun patch without writing the portability loss,
- stay trapped in one family because it is easy to tune,
- skip targeted literature follow-up when reflection has exposed a real gap and instead reinvent old sampler ideas blindly,
- limit targeted follow-up search to repo-provided or already-named methods once reflection has shown a real gap,
- treat literature search as a box-checking ritual,
- read only abstracts or summaries when the method details matter,
- use a paper as a primary anchor without downloading and reading its PDF,
- proceed when the literature workspace still lacks the required paper-note pseudocode,
- replay named methods from papers without extracting a repo-suited mechanism idea,
- waste budget on repeated full paper sweeps beyond the official protocol,
- claim poster-level progress without a paper-path win over Heun,
- bury the real idea under many unrelated stabilizers.

The goal is not to produce a complicated sampler. The goal is not to reproduce a literature survey inside `sample.py`. The goal is to produce a **defensible, simple, externally grounded mechanism** that survives the official evaluation path.
