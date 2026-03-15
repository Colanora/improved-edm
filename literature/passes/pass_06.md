# Literature Pass pass_06

pass_id=pass_06
session_date=2026-03-15
working_paper_base=e2379ec
trigger=the same-family STORK widening ablation weakened already on the 5k proxy, so `program.md` now wants the next branch to pair incumbent consolidation with an orthogonal literature-grounded family rather than more window widening.
paper_refs=bns_2024, diff_solver_search_2025, consistency_solver_2025
candidate_families=localized_pfdiff_springboard_predictor

## Consulted Papers

- [`bns_2024`](../papers/bns_2024.md)
- [`diff_solver_search_2025`](../papers/diff_solver_search_2025.md)
- [`consistency_solver_2025`](../papers/consistency_solver_2025.md)

## Session Takeaway


- The three fresh papers reinforce the same hard boundary from different angles: BNS, differentiable solver search, and ConsistencySolver all improve few-step sampling by learning or searching step-specific solver parameters, which is real evidence that coefficient placement matters, but it is out of scope for this repo.
- Re-reading `PFDiff` and `FSampler` after the STORK widening miss sharpens a different portable residue: cached past information can still help even without learned coefficients if it is used to reposition a single late predictor state, not to skip calls, learn schedules, or globally rewrite the solver.
- `PFDiff` is especially instructive for higher-order solvers because, once the solver order is above 1, the paper drops the future-score anticipation and keeps only the past-score springboard. That is exactly the part that can be localized into this repo.
- With `e2379ec` now established as both the paper winner and the minimal STORK placement, the next orthogonal probe should keep the `{4}` midpoint plus `{3}` UniPC tail unchanged and replace the `{5}` virtual-drift construction with a past-score springboard at the predictor state.


## Candidate Card


family=localized_pfdiff_springboard_predictor
kind=mechanism
external_anchor=PFDiff: Training-Free Acceleration of Diffusion Models Combining Past and Future Scores (Wang et al., 2025); FSampler: Training-Free Acceleration of Diffusion Sampling via Epsilon Extrapolation (Vladimir, 2025)
borrowed_mechanism=use cached past denoising information to create a guarded one-step springboard state before the next real predictor evaluation, while keeping the full NFE budget and the downstream solver structure unchanged
synthesis_step=from the exact `e2379ec` paper base, disable the STORK virtual-drift branch on the single `{steps_left=5}` approach step and instead set the predictor-state evaluation point to a PFDiff-style springboard `x_spring = x_hat + alpha * h * prev_d_prime`, reusing the previous accepted slope as the past-score guide; keep the `{4}` midpoint entry step, `{3}` UniPC corrector, and terminal exact-Heun pair unchanged
portability=direct
base_commit=e2379ec
active_nf_range=paper-targeted late full-step regime only; NFE 5/9/11/13 should remain inside the stable dormant band because the branch is inactive when `num_steps < 12`
extra_nfe=0
hypothesis=the remaining full-step error may be predictor-state placement rather than predictor-slope extrapolation; a single past-score springboard could feed the winning midpoint-plus-UniPC tail with a better entering state without widening the STORK residue or touching the low-NFE frontier
expected_signature=the proxy frontier should remain in the usual stable band; if promoted, paper block 0 should stay near or improve on the `e2379ec` base `1.92366`, while a clear loss would reject the springboard-state family as less portable than the virtual-drift family
ablation=if this family shows life, compare the same `{5}` placement using `prev_d_cur` instead of `prev_d_prime` so we can separate accepted-slope springboarding from raw-drift reuse
kill_condition=any low-NFE drift outside the stable band, any instability, or any paper block-0 loss that clearly trails the `e2379ec` base
