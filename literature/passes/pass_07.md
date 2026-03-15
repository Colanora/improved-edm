# Literature Pass pass_07

pass_id=pass_07
session_date=2026-03-15
working_paper_base=e2379ec
trigger=the localized residualized virtual-predictor family spent its justified follow-up and closed with a clear proxy loss on `ca28f14`, so `program.md` requires another fresh external literature rotation before the next family.
paper_refs=tap_2026, etc_2025, sada_2025
candidate_families=localized_trend_consistent_virtual_predictor

## Consulted Papers

- [`tap_2026`](../papers/tap_2026.md)
- [`etc_2025`](../papers/etc_2025.md)
- [`sada_2025`](../papers/sada_2025.md)

## Session Takeaway


- `TAP` is a clean architectural reject boundary: token-adaptive predictor selection is real, but it depends on internal layer hooks and cannot be faithfully compressed into a `sample.py`-only sampler.
- `ETC` gives the strongest direct residue for this repo: the right correction signal may be a recursively smoothed historical denoising trend, not the raw one-step residual that recent local families keep reusing.
- `SADA` corroborates the same direction from the solver side: when approximations help, they help by respecting the ODE trajectory and using structured historical gradient information rather than ad hoc reuse.
- The next direct family should therefore keep the exact `e2379ec` paper base and replace the single-step STORK history vector on the `{steps_left=5}` predictor step with a recursively smoothed trend built from recent drift differences.


## Candidate Card


family=localized_trend_consistent_virtual_predictor
kind=mechanism
external_anchor=ETC: Training-Free Diffusion Models Acceleration with Error-Aware Trend Consistency (Xie et al., 2025); SADA: Stability-guided Adaptive Diffusion Acceleration (Jiang et al., 2025)
borrowed_mechanism=replace the raw one-step late predictor trend with a recursively smoothed historical trend, preserving long-horizon direction while damping error-corrected fluctuations
synthesis_step=from the exact `e2379ec` paper base, keep the single `{steps_left=5}` virtual-predictor placement but introduce a recursive trend state `trend_cur = (1 - alpha) * trend_prev + alpha * (d_cur - prev_d_cur)` (initialized from the first available drift difference) and use that trend instead of `(d_cur - prev_d_cur)` inside the localized virtual predictor; keep the `{4}` midpoint entry step, `{3}` UniPC corrector, and terminal exact-Heun pair unchanged everywhere else
portability=direct
base_commit=e2379ec
active_nf_range=paper-targeted late full-step regime only; NFE 5/9/11/13 should remain in the usual dormant band because the modified branch is still inactive when `num_steps < 12`
extra_nfe=0
hypothesis=the current paper winner may still be slightly too sensitive to the most recent drift fluctuation on the approach step; using a recursively smoothed trend should preserve the useful late-direction information while damping the low-NFE softness that keeps appearing when raw history is perturbed
expected_signature=the proxy frontier should at least match the dormant-band stability of `e2379ec` while improving the late full-step signal; compared with the closed residualized family, the `NFE=5` point should stay tighter to base instead of softening
ablation=if this shows life, compare the same smoothed-trend construction using `(d_cur - prev_d_prime)` as the incoming trend increment, so we can separate smoothing from raw-drift history choice
kill_condition=any clear proxy loss versus `e2379ec`, any low-NFE drift outside the usual dormant band, or any sign that the smoothed trend simply behaves like another closed STORK-history tweak rather than a new family


## Candidate Card


family=localized_trend_consistent_virtual_predictor
kind=ablation
external_anchor=ETC: Training-Free Diffusion Models Acceleration with Error-Aware Trend Consistency (Xie et al., 2025); SADA: Stability-guided Adaptive Diffusion Acceleration (Jiang et al., 2025)
borrowed_mechanism=keep the recursive trend smoother but swap the previous-history anchor from the raw prior drift to the accepted prior corrected slope
synthesis_step=from commit `de25906`, keep the localized `{steps_left=5}` trend-consistent virtual predictor exactly as-is but change the incoming trend increment from `(d_cur - prev_d_cur)` to `(d_cur - prev_d_prime)` whenever the accepted previous slope is available, leaving the recursive smoothing coefficient, `{4}` midpoint entry step, `{3}` UniPC corrector, and terminal exact-Heun pair unchanged
portability=direct
base_commit=de25906
active_nf_range=paper-targeted late full-step regime only; NFE 5/9/11/13 should remain in the usual dormant band because only the single late predictor trend source changes
extra_nfe=0
hypothesis=the positive proxy sign suggests the smoothed trend itself is useful, but the current raw-drift increment may still be slightly stale for the lowest NFE point; anchoring the trend increment to the accepted previous slope could preserve the mid-band gains while tightening `NFE=5`
expected_signature=the frontier should improve on `de25906 = 2.607512` or at least keep the win while reducing the `NFE=5` softness; a reversal at `NFE=9`/`NFE=13` would mean the family is another fragile history tweak
ablation=if this loses clearly, close the trend-consistent family rather than stacking smoothing-factor scans
kill_condition=any clear proxy loss versus both `de25906` and `e2379ec`, any new instability, or any broader low-NFE drift outside the usual dormant band
