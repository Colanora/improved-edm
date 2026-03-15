# Literature Pass pass_04

pass_id=pass_04
session_date=2026-03-14
working_paper_base=5e43179
trigger=the localized RX-DPM approach also failed on paper block 0, so the next rotation must avoid schedule-only, endpoint-placement, and block-extrapolation mechanisms.
paper_refs=sdm_2026, dual_solver_2026, dpm_solver_2022, rex_2026, fscheduler_2026, fsampler_2025, tap_2026, pdns_2025
candidate_families=curvature_gated_late_exactization, localized_dpm_solver2_preterminal_midpoint, embedded_proximal_midpoint_trust_region

## Consulted Papers

- [`sdm_2026`](../papers/sdm_2026.md)
- [`dual_solver_2026`](../papers/dual_solver_2026.md)
- [`dpm_solver_2022`](../papers/dpm_solver_2022.md)
- [`rex_2026`](../papers/rex_2026.md)
- [`fscheduler_2026`](../papers/fscheduler_2026.md)
- [`fsampler_2025`](../papers/fsampler_2025.md)
- [`tap_2026`](../papers/tap_2026.md)
- [`pdns_2025`](../papers/pdns_2025.md)

## Session Takeaway


- `SDM` contributes a direct, zero-extra-NFE cache-based curvature gate that is still open in this repo because it changes *when* a stronger step is used rather than changing the schedule or introducing a new endpoint formula.
- `Dual-Solver` is a clean reject boundary: learned per-step coefficients and learned timesteps are out of scope even though the inference-time predictor-corrector pattern looks familiar.
- `DPM-Solver` provides the older solver-design reference for why late curvature should trigger a more exact step, but not necessarily a global solver swap.
- The next clean synthesized target is therefore a conservative curvature-gated exactization step immediately before the existing `{3,4}` UniPC window, leaving the paper-qualified tail structure intact.


## Candidate Card


family=curvature_gated_late_exactization
kind=mechanism
external_anchor=Formalizing the Sampling Design Space of Diffusion-Based Generative Models via Adaptive Solvers and Wasserstein-Bounded Timesteps (Jo & Choi, 2026); DPM-Solver (Lu et al., 2022)
borrowed_mechanism=use a cached relative-curvature proxy to decide when a late step should be promoted from a cheaper approximate update to a more exact higher-order one
synthesis_step=keep the exact `5e43179` sampler everywhere, including the `{3,4}` localized UniPC window and the last two exact-Heun stages, but add an SDM-style sample-wise curvature gate on non-UniPC late standard steps that collapses the current relaxed predictor-corrector update to exact Heun only when the cached relative curvature exceeds a conservative threshold
portability=direct
base_commit=6b1e3f6
active_nf_range=paper-targeted full-step regime only; the branch is dormant when `num_steps < 12`, so NFE 5/9/11/13 should remain unchanged
extra_nfe=0
hypothesis=the current paper winner may only need extra exactness on the single high-curvature step immediately before the `{3,4}` UniPC window, and a curvature trigger can supply that selectively without reopening the failures from fixed schedule warps, forward-value placement, or block extrapolation
expected_signature=the proxy frontier at NFE 5/9/11/13 stays inside the current stable band while `fid_N35` improves below `6.7513`; if promoted, paper block 0 should beat `1.93345` or at least show a cleaner same-sign move than the recent misses
ablation=if this wins, compare against the same code path with the curvature threshold raised high enough to disable the gate, to isolate the gain from the adaptive trigger rather than from incidental refactoring
kill_condition=any `fid_N35` regression, any low-NFE drift outside the stable band, or any paper block-0 miss that looks like another clear translation failure


## Candidate Card


family=localized_dpm_solver2_preterminal_midpoint
kind=mechanism
external_anchor=DPM-Solver (Lu et al., 2022); Formalizing the Sampling Design Space of Diffusion-Based Generative Models via Adaptive Solvers and Wasserstein-Bounded Timesteps (Jo & Choi, 2026)
borrowed_mechanism=replace one late higher-order step with a dedicated lambda-midpoint DPM-Solver-2 update that analytically targets the diffusion ODE structure rather than using a generic endpoint corrector
synthesis_step=keep the exact `5e43179` base everywhere except the first pre-terminal `{steps_left=4}` UniPC step; on that single step, replace the local UniPC correction with a VE-form DPM-Solver-2 midpoint update in log-SNR/lambda midpoint sigma, while preserving the second `{steps_left=3}` UniPC step and the last two exact-Heun stages
portability=direct
base_commit=24aa494
active_nf_range=paper-targeted full-step regime only; the branch is dormant when `num_steps < 12`, so NFE 5/9/11/13 should remain unchanged
extra_nfe=0
hypothesis=the two-step `{3,4}` paper-qualified window may still need two distinct late mechanisms: a dedicated midpoint exponential-integrator step at `{4}` to enter the terminal zone cleanly, followed by the existing history-aware UniPC correction at `{3}`
expected_signature=the proxy frontier at NFE 5/9/11/13 stays inside the current stable band; if promoted, paper block 0 should improve over `1.93345` or at least beat the recent exactization miss and justify a full-row continuation
ablation=if this wins, compare against the same code path with the midpoint branch disabled so `{4}` falls back to the original UniPC step, isolating whether the gain comes from the midpoint solver itself rather than from refactoring
kill_condition=any low-NFE drift outside the stable band, any proxy instability, or any paper block-0 result that clearly trails the `5e43179` base


## Candidate Card


family=localized_dpm_solver2_preterminal_midpoint
kind=ablation
external_anchor=DPM-Solver (Lu et al., 2022)
borrowed_mechanism=keep the same dedicated lambda-midpoint solver substitution but move its placement within the two-step pre-terminal window
synthesis_step=from the new paper base `3d0ecd6`, relocate the localized DPM-Solver-2 midpoint branch from `{steps_left=4}` to `{steps_left=3}` so the earlier step falls back to the original UniPC correction while the later pre-terminal step takes the midpoint solver update
portability=direct
base_commit=1d36e19
active_nf_range=paper-targeted full-step regime only; the branch remains dormant when `num_steps < 12`
extra_nfe=0
hypothesis=if the win is truly tied to the *placement* of the midpoint solver on the first pre-terminal step, then moving it one step later should weaken the paper path even if the proxy band stays effectively unchanged
expected_signature=the proxy frontier remains inside the usual stable band; if promoted, paper block 0 should land above the new `3d0ecd6` base `1.92757`, confirming that the step-4 placement is the active ingredient
ablation=this is the first same-family placement ablation required after the paper promotion; if it weakens, the current `3d0ecd6` story becomes much sharper
kill_condition=any low-NFE drift outside the stable band, any proxy instability, or any paper block-0 result that is not clearly weaker than `3d0ecd6`


## Candidate Card


family=localized_dpm_solver2_preterminal_midpoint
kind=ablation
external_anchor=DPM-Solver (Lu et al., 2022)
borrowed_mechanism=keep the same dedicated lambda-midpoint solver substitution but widen it across the entire two-step pre-terminal window
synthesis_step=from the restored `3d0ecd6` paper base, activate the localized DPM-Solver-2 midpoint branch on both `{steps_left=4}` and `{steps_left=3}` so the full pre-terminal tail becomes a two-step midpoint-solver block and the history-aware UniPC correction is removed only inside that window
portability=direct
base_commit=c0f176b
active_nf_range=paper-targeted full-step regime only; the branch remains dormant when `num_steps < 12`
extra_nfe=0
hypothesis=if the `3d0ecd6` gain comes mostly from introducing midpoint diffusion-ODE structure anywhere in the pre-terminal tail, then widening the midpoint branch to both late steps could preserve or improve the paper path; if it weakens, the mixed midpoint-at-`{4}` plus UniPC-at-`{3}` composition is the real mechanism
expected_signature=the proxy frontier should remain inside the usual stable band; if promoted, paper block 0 will likely land above `1.92757` if the mixed tail is minimal, but a surprise improvement would argue that the second late step also prefers midpoint integration over history correction
ablation=this is the complementary same-family consolidation probe after the `{steps_left=3}` placement miss; together the two ablations test whether placement or two-step widening can explain the paper win
kill_condition=any low-NFE drift outside the stable band, any proxy instability, or any paper block-0 result that clearly trails the `3d0ecd6` base


## Session Takeaway


- `Rex` closes off another tempting transformed-RK branch: its genuinely new part is reversibility with a shadow state, while the forward-only portable core mostly collapses back into DDIM/DPM/SEEDS-style exponential-integrator solvers.
- `F-scheduler` is a clean reject boundary for schedule work that depends on decoder tolerance, latent truncation, or Free-U U-Net decoration rather than on a pure sampler-side mechanism.
- `FSampler` and `TAP` are both strong evidence that many recent diffusion speedups come from changing NFE accounting or model-internal adaptive compute, not from a same-budget sampler update; the only portable residue is disagreement-based confidence signaling.
- `PDNS` is incompatible as a direct method, but its proximal viewpoint suggests a new in-bounds synthesis: keep a higher-order step only when its embedded local error is small, and otherwise shrink it toward a simpler companion without changing NFE.
- The next clean synthesized target is therefore an embedded trust-region family on top of the current `3d0ecd6` base: use the free Euler-vs-midpoint disagreement inside the existing DPM entry step as a local trust signal, and proximal-shrink the midpoint update toward its first-order companion when the embedded error is large.


## Candidate Card


family=embedded_proximal_midpoint_trust_region
kind=mechanism
external_anchor=Proximal Diffusion Neural Sampler (Guo et al., 2025); Rex: A Family of Reversible Exponential (Stochastic) Runge-Kutta Solvers (Blasingame & Liu, 2026)
borrowed_mechanism=combine a proximal conservative-update idea with an embedded Euler-versus-midpoint pair that provides a free local error signal inside the same two-call DPM-style step
synthesis_step=keep the exact `3d0ecd6` paper base everywhere, but on the pre-terminal `{steps_left=4}` midpoint branch compute both the first-order Euler companion and the second-order midpoint update, then use their normalized disagreement to shrink the midpoint proposal back toward the Euler companion when the embedded local error is large, without changing NFE or the downstream `{steps_left=3}` UniPC correction
portability=direct
base_commit=1705480
active_nf_range=paper-targeted full-step regime only; the branch remains dormant when `num_steps < 12`
extra_nfe=0
hypothesis=the `3d0ecd6` win may contain a real midpoint-direction benefit but still overshoot on a subset of trajectories; an embedded trust-region shrink could preserve the good direction while damping the rare over-aggressive step, potentially improving paper block 0 without reopening the wide misses from placement or whole-window rewrites
expected_signature=the low-NFE proxy band should stay inside the usual dormant range; if promoted, paper block 0 should beat `1.92757` or at least sit materially closer to the base than the `{3}`-placement and `{3,4}`-widening ablation losses
ablation=if this wins, rerun with the trust shrink disabled to recover exact `3d0ecd6`, and with a fixed constant shrink weight, to verify that adaptive embedded-error control rather than simple under-relaxation is the active ingredient
kill_condition=any low-NFE drift outside the stable band, any proxy instability, or any paper block-0 result that clearly loses to `3d0ecd6`


## Candidate Card


family=embedded_proximal_midpoint_trust_region
kind=tuning
external_anchor=Proximal Diffusion Neural Sampler (Guo et al., 2025); Rex: A Family of Reversible Exponential (Stochastic) Runge-Kutta Solvers (Blasingame & Liu, 2026)
borrowed_mechanism=keep the same embedded Euler-versus-midpoint trust-region idea but weaken the maximum proximal shrink after the first full-row result showed a small, same-sign over-damping
synthesis_step=from the restored `3d0ecd6` base, reintroduce the embedded midpoint trust-region branch exactly as in `5ef8741` but reduce the maximum shrink cap from `0.35` to `0.20`, leaving the disagreement formula and every other sampler component untouched
portability=direct
base_commit=f45c798
active_nf_range=paper-targeted full-step regime only; the branch remains dormant when `num_steps < 12`
extra_nfe=0
hypothesis=if the first trust-region probe lost only because it damped the good midpoint correction too aggressively, then a smaller cap should preserve the near-tie behavior while giving back enough midpoint strength to beat the `3d0ecd6` mean
expected_signature=the low-NFE proxy band should remain in the usual dormant range; if promoted, the paper row should stay near the incumbent on blocks 0 and 1 while improving block 2 enough to recover the mean gap
ablation=this is the one allowed scalar follow-up after the initial full-row near-tie; if it also loses, stop tuning the trust cap and rotate away from the family
kill_condition=any low-NFE drift outside the stable band, any proxy instability, or any paper row that remains clearly worse than the `3d0ecd6` base
