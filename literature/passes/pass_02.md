# Literature Pass pass_02

pass_id=pass_02
session_date=2026-03-14
working_paper_base=5e43179
trigger=the localized schedule-law family missed decisively on paper block 0, so the next rotation must come from a different direct mechanism family.
paper_refs=forward_value_2026, ltc_accel_2025
candidate_families=localized_forward_value_approach

## Consulted Papers

- [`forward_value_2026`](../papers/forward_value_2026.md)
- [`ltc_accel_2025`](../papers/ltc_accel_2025.md)

## Session Takeaway


- `Fast Forward-Value` is the most promising new direct family after the schedule-law miss because it changes evaluation placement rather than adding another history buffer or requiring offline search.
- `LTC-Accel` is useful mostly as a reject boundary: it is training-free, but its benefit comes from skipping denoiser evaluations, which is outside this repo's fixed-NFE contract.
- The next clean synthesized target is therefore a localized forward-value branch that changes only how the late approach steps use the already-available endpoint evaluation, while keeping the `5e43179` pre-terminal UniPC window and terminal exact-Heun pair intact.


## Candidate Card


family=localized_forward_value_approach
kind=mechanism
external_anchor=Are First-Order Diffusion Samplers Really Slower? A Fast Forward-Value Approach (Jiao et al., 2026)
borrowed_mechanism=replace a backward-value or symmetric late update with a forward-value update that evaluates the model at a cheap one-step lookahead estimate of the next state
synthesis_step=keep the `5e43179` base unchanged on the `{3,4}` localized UniPC window and terminal exact-Heun pair, but on the two earlier approach steps immediately before that window use the already available endpoint evaluation to take a localized forward-value update instead of the current Heun-style blended slope
portability=direct
base_commit=2510eb1
active_nf_range=paper-targeted late full-step regime only; the low-NFE frontier should remain unchanged because the branch is dormant when `num_steps < 12`
extra_nfe=0
hypothesis=the winning `5e43179` trajectory may still enter the `{3,4}` UniPC window with the wrong signed approach error; a localized forward-value step on the earlier approach interval could improve that entry without another history-compensation branch or a global solver swap
expected_signature=the proxy frontier at NFE 5/9/11/13 stays effectively unchanged; if promoted to paper, block 0 should improve over `1.93345` or at least show a clear same-sign move before spending more paper budget
ablation=if this wins, compare against the same window with the existing Heun-style blended slope and against a pure endpoint-Euler variant with no lookahead reuse, to isolate whether the gain is truly from forward-value placement
kill_condition=any paper block-0 loss that looks like another large translation failure, any unexpected low-NFE drift, or a result that is indistinguishable from the already-rejected late schedule-law family
