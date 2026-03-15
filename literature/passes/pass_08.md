# Literature Pass pass_08

pass_id=pass_08
session_date=2026-03-15
working_paper_base=e2379ec
trigger=the orthogonal adaptive-allocation family lost cleanly on proxy, so `program.md` requires a fresh 3-paper external literature rotation before another family change.
paper_refs=s4s_2025, tada_2025, aflops_2026
candidate_families=localized_residualized_virtual_predictor

## Consulted Papers

- [`s4s_2025`](../papers/s4s_2025.md)
- [`tada_2025`](../papers/tada_2025.md)
- [`aflops_2026`](../papers/aflops_2026.md)

## Session Takeaway


- `S4S` is a strong negative boundary: learned time-dependent solver coefficients are genuinely useful at very low NFE, but the repo cannot promote an offline teacher-distilled coefficient search as a `sample.py`-only poster mechanism.
- `TADA` makes the augmented-dynamics lesson sharper without forcing a full momentum rewrite: what transfers cleanly is not another global latent augmentation, but the idea that late-step dynamics contain a large state-aligned linear component plus a smaller innovation term.
- `A-FloPS` contributes the missing direct formula: estimate a local scalar `lambda` from consecutive state and drift changes, subtract `lambda x`, and extrapolate the residual only. That gives a clean synthesized family which is more structural than another scalar gate yet still lives entirely inside the existing `e2379ec` late-step STORK window.


## Candidate Card


family=localized_residualized_virtual_predictor
kind=mechanism
external_anchor=A-FloPS: Accelerating Diffusion Models via Adaptive Flow Path Sampler (Jin et al., 2026); TADA: Improved Diffusion Sampling with Training-free Augmented DynAmics (Chen et al., 2025)
borrowed_mechanism=estimate a local state-aligned linear drift and extrapolate only the residual innovation, instead of extrapolating the whole late-step drift vector
synthesis_step=from the exact `e2379ec` paper base, keep the single `{steps_left=5}` STORK virtual-predictor placement but replace the raw history difference `(d_cur - prev_d_cur)` with a residualized difference `[(d_cur - lambda * x_hat) - (prev_d_cur - lambda * prev_x_hat)]`, where `lambda = <d_cur - prev_d_cur, x_hat - prev_x_hat> / ||x_hat - prev_x_hat||^2` is estimated per sample and clamped for stability; keep the `{4}` midpoint entry step, `{3}` UniPC corrector, and terminal exact-Heun pair unchanged
portability=direct
base_commit=e2379ec
active_nf_range=paper-targeted late full-step regime only; NFE 5/9/11/13 should remain in the usual dormant band because the residualized branch is inactive when `num_steps < 12`
extra_nfe=0
hypothesis=the paper-winning STORK virtual predictor may still be carrying too much of the late PF-ODE radial contraction term; subtracting a locally estimated state-aligned linear drift before extrapolation should isolate the true innovation and yield a cleaner predictor state on the single approach step
expected_signature=the proxy frontier should at least recover the dormant-band behavior of the base while improving the late full-step read; if the decomposition is right, `NFE=5` should stop softening versus the base and block-0 paper quality should remain near `1.92366` or better
ablation=if this shows life, test the same residualized virtual predictor with `prev_d_prime` instead of `prev_d_cur` as the previous-velocity term to separate residualization from raw-drift history choice
kill_condition=any clear proxy loss versus `e2379ec`, any low-NFE drift outside the normal dormant band, or any instability from the local `lambda` estimate


## Candidate Card


family=localized_residualized_virtual_predictor
kind=ablation
external_anchor=A-FloPS: Accelerating Diffusion Models via Adaptive Flow Path Sampler (Jin et al., 2026); TADA: Improved Diffusion Sampling with Training-free Augmented DynAmics (Chen et al., 2025)
borrowed_mechanism=keep the local linear-plus-residual decomposition but swap which previous velocity anchors the residual history
synthesis_step=from commit `e68bac4`, keep the localized `{steps_left=5}` residualized virtual predictor exactly as-is but replace the previous raw drift term in the residual history with the previous accepted slope `prev_d_prime`, i.e. use `[(d_cur - lambda * x_hat) - (prev_d_prime - lambda * prev_x_hat)]` while keeping the same per-sample `lambda` estimate, `{4}` midpoint entry step, `{3}` UniPC corrector, and terminal exact-Heun pair unchanged
portability=direct
base_commit=e68bac4
active_nf_range=paper-targeted late full-step regime only; NFE 5/9/11/13 should remain in the usual dormant band because only the single late virtual-predictor branch changes
extra_nfe=0
hypothesis=the near-tie proxy result suggests the residualization itself is sound, but the raw previous drift may still be slightly stale once the prior step has already been corrected; using the previous accepted slope could preserve the `NFE=9`/`NFE=11` gains while recovering the soft `NFE=5` point
expected_signature=the frontier score should improve past `2.607519` and ideally match or beat the base `2.607516`; if the family is real, the band should keep the mid-NFE gains without paying the same `NFE=5` penalty
ablation=if this loses clearly, close the residualized family rather than stacking clamp or weighting tweaks
kill_condition=any clear frontier regression versus both `e68bac4` and `e2379ec`, any new instability, or any broader low-NFE drift outside the normal dormant band
