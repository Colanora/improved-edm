# Literature Pass pass_14

pass_id=pass_14
session_date=2026-03-15
working_paper_base=e2379ec
trigger=pass_13 concluded that no clean unused direct anchor remained in the reviewed pool, so a targeted follow-up search was required before the next serious experiment.
pass_kind=targeted_followup
followup_question=What recent deterministic diffusion-ODE sampler mechanism can still be expressed as a simple zero-extra-NFE local update inside `sample.py`, is mechanistically distinct from late history-vector/state-placement tweaks, and does not rely on learned coefficients, offline model statistics, stochasticity, or a global schedule/flow rewrite?
paper_refs=erk_guid_2026
candidate_families=localized_erk_guided_terminal_heun

## Consulted Papers

- [`erk_guid_2026`](../papers/erk_guid_2026.md)

## Session Takeaway


- The targeted follow-up found a genuinely new direct anchor dated 2026-03-04: `ERK-Guid`, which uses embedded Euler-vs-Heun solver discrepancies as a cost-free stiffness and dominant-error-direction signal.
- This is the first clean reviewed paper in the current loop whose portable core is neither a late history-vector tweak nor an offline/search-based solver family.
- The most repo-suited residue is not the paper's whole guidance framing; it is a localized stiffness-gated correction on an existing exact-Heun pair already present in the `e2379ec` terminal tail.
- Because the base sampler already contains two terminal exact-Heun stages, the simplest first probe is to cache the Euler companion from the first exact-Heun stage and use it to guide the second exact-Heun stage only.


## Candidate Card


family=localized_erk_guided_terminal_heun
kind=mechanism
external_anchor=Error as Signal: Stiffness-Aware Diffusion Sampling via Embedded Runge-Kutta Guidance (Kong et al., 2026)
borrowed_mechanism=estimate local stiffness and dominant truncation-error direction from the cached Euler-vs-Heun discrepancy of one exact-Heun step, then apply a gated correction along that direction on the next exact-Heun step without extra NFE
synthesis_step=from the exact `e2379ec` paper base, keep the `{5}` STORK virtual predictor, `{4}` midpoint entry step, `{3}` UniPC corrector, and the two terminal exact-Heun stages unchanged, but cache the Euler companion and Euler drift from the first terminal exact-Heun step and apply an ERK-Guid-style correction `x_next = x_heun - h * beta * z^2 * <d_cur, v_hat> v_hat` on the following terminal exact-Heun step with `w_con=0.5` and `w_stiff=0.75`
portability=direct
base_commit=e2379ec
active_nf_range=paper-targeted late full-step regime only; the mechanism is dormant when `num_steps < 12`, so proxy NFE 5/9/11/13 should remain unchanged
extra_nfe=0
hypothesis=the current paper base already fixed terminal order mismatch with exact Heun, but the remaining full-row gap may still be a stiffness-aligned truncation error on the second terminal exact-Heun stage; a localized ERK correction can suppress that error without disturbing the earlier winning tail structure
expected_signature=the 5k proxy should stay tied with `e2379ec`, while the authoritative paper row should improve modestly if the penultimate exact-Heun stage still carries a stiffness-aligned error
ablation=if the family shows life, rerun with the same cache plumbing but `w_stiff=0` to verify that any gain comes from the ERK correction rather than from incidental refactoring
kill_condition=any instability, any proxy drift outside dormant noise, or any paper block-0 loss that clearly trails `e2379ec`
