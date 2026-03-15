# Literature Pass pass_05

pass_id=pass_05
session_date=2026-03-14
working_paper_base=3d0ecd6
trigger=the embedded midpoint trust-region family produced two full-row paper losses, so `program.md` requires a fresh literature rotation before the next family change.
paper_refs=score_normalization_2023, dyweight_2026, stork_2025
candidate_families=localized_online_score_normalized_approach, localized_stork_virtual_predictor

## Consulted Papers

- [`score_normalization_2023`](../papers/score_normalization_2023.md)
- [`dyweight_2026`](../papers/dyweight_2026.md)
- [`stork_2025`](../papers/stork_2025.md)

## Session Takeaway


- `DyWeight` reinforces a hard reject boundary: few-step solver coefficients and time shifts really do want to be step-specific, but learning them offline is out of scope here.
- `STORK` shows a second hard boundary: structure-independent stiff solvers can help, but the practical route uses many virtual substeps and bootstrap logic, which is too global and too complex to be the next clean repo mechanism.
- `Score Normalization for a Faster Diffusion Exponential Integrator Sampler` exposes a more portable residue than the current compensation family: late-stage error can come from score-magnitude miscalibration itself, not only from the direction of the history term.
- The previous `DualFast` / `DC-Solver` branch already rejected additive current-score and buffer compensation on the approach steps, so the next family should not be another additive history blend.
- The next clean synthesized target is therefore a localized online score-normalization family on top of `3d0ecd6`: keep the winning `{4}` midpoint plus `{3}` UniPC tail fixed, and calibrate only the two earlier approach steps with an online drift-norm reference rather than a learned or offline schedule.


## Candidate Card


family=localized_online_score_normalized_approach
kind=mechanism
external_anchor=Score Normalization for a Faster Diffusion Exponential Integrator Sampler (Xia et al., 2023); DyWeight: Dynamic Gradient Weighting for Few-Step Diffusion Sampling (Zhao et al., 2026)
borrowed_mechanism=time-varying score/gradient scale calibration so the fast solver sees a better-conditioned late integrand without extra model evaluations
synthesis_step=from the exact `3d0ecd6` paper base, keep the `{steps_left=4}` DPM-Solver-2 midpoint step and the `{steps_left=3}` UniPC corrector untouched, but on the two earlier approach steps `{5,6}` rescale the current drift toward the recent accepted-drift magnitude using an online per-sample norm reference from `prev_d_prime`, capped by the existing late predictor-ramp magnitude instead of a learned/offline table
portability=direct
base_commit=3d0ecd6
active_nf_range=paper-targeted late full-step regime only; NFE 5/9/11/13 should stay inside the usual dormant band because the branch is inactive when `num_steps < 12`
extra_nfe=0
hypothesis=the remaining paper gap may be a late approach-step scale-calibration problem rather than another direction or schedule problem; online norm calibration should feed the winning midpoint-plus-UniPC tail with a better-conditioned state while leaving the low-NFE frontier unchanged
expected_signature=the proxy frontier should remain inside the usual stable band; if promoted, paper block 0 should improve beyond the `3d0ecd6` base `1.92757` or at least outperform the recent trust-region near-ties
ablation=if this family wins, keep the same `{5,6}` window but replace the online norm ratio with a constant `1.0` or a fixed scalar so we can distinguish true online calibration from the mere existence of another late branch
kill_condition=any low-NFE drift outside the stable band, any instability on the approach steps, or any paper block-0 loss that clearly trails the `3d0ecd6` base


## Candidate Card


family=localized_stork_virtual_predictor
kind=mechanism
external_anchor=STORK: Faster Diffusion And Flow Matching Sampling By Resolving Both Stiffness And Structure-Dependence (Tan et al., 2025)
borrowed_mechanism=replace one late predictor evaluation with a virtual internal stage synthesized from the current drift and a finite-difference time derivative estimated from the previous real drift
synthesis_step=from the exact `3d0ecd6` base, keep the `{steps_left=4}` midpoint entry step and `{steps_left=3}` UniPC corrector untouched, but on the single earlier approach step `{5}` replace the usual relaxed predictor extrapolation with a STORK-inspired virtual predictor `d_virtual` at the predictor time, using `prev_d_cur` and `prev_h` to approximate the local time derivative without adding model calls
portability=direct
base_commit=3d0ecd6
active_nf_range=paper-targeted late full-step regime only; NFE 5/9/11/13 should remain in the dormant band because the branch is inactive when `num_steps < 12`
extra_nfe=0
hypothesis=the current paper base may still lose accuracy on the single standard-regime step immediately before the winning midpoint entry; a virtual internal stage tied to the actual predictor time could improve stiffness handling there without modifying the midpoint-plus-UniPC tail itself
expected_signature=the proxy frontier should stay in the usual stable band; if promoted, paper block 0 should land below `1.92757` or at least beat the recent `abb8a61` paper-side loss convincingly
ablation=if this family wins, keep the same `{5}` window but fall back to the original predictor extrapolation rule to verify that the gain comes from the virtual-stage construction rather than from another late-branch placement
kill_condition=any low-NFE drift outside the stable band, any instability, or any paper block-0 loss that clearly trails the `3d0ecd6` base


## Candidate Card


family=localized_stork_virtual_predictor
kind=tuning
external_anchor=STORK: Faster Diffusion And Flow Matching Sampling By Resolving Both Stiffness And Structure-Dependence (Tan et al., 2025)
borrowed_mechanism=apply the same virtual-stage predictor on a slightly wider late approach window to test whether the structural stiffening benefit is truly single-step or shared across the two late approach steps
synthesis_step=from the new paper base `e2379ec`, widen `RESEARCH_STANDARD_LOCAL_VIRTUAL_PREDICTOR_STEPS_LEFT` from `(5,)` to `(5, 6)` while keeping the virtual-stage formula, the `{4}` midpoint entry step, and the `{3}` UniPC corrector unchanged
portability=direct
base_commit=e2379ec
active_nf_range=paper-targeted late full-step regime only; NFE 5/9/11/13 should remain in the dormant band because the branch is still inactive when `num_steps < 12`
extra_nfe=0
hypothesis=if the STORK-style virtual-stage effect is really correcting late-step stiffness rather than one lucky placement, widening it across both approach steps `{5,6}` could preserve or slightly improve the paper row; if it weakens, the current `{5}`-only placement is the minimal transferable mechanism
expected_signature=the proxy frontier should remain in the usual stable band; if promoted, the paper row should stay near or beat `e2379ec`, while a clear loss would identify `{5}` as the active placement
ablation=this is the natural placement follow-up after the paper win; if it weakens, treat the current `{5}`-only branch as the minimal defensible family and stop widening this mechanism
kill_condition=any low-NFE drift outside the stable band, any instability, or any paper block-0 result that clearly trails the `e2379ec` base
