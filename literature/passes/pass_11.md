# Literature Pass pass_11

pass_id=pass_11
session_date=2026-03-15
working_paper_base=e2379ec
trigger=the PFDiff-style springboard family produced two consecutive proxy misses, so `program.md` requires a fresh literature rotation before another family change.
paper_refs=amed_solver_2024, sa_solver_2025
candidate_families=localized_amed_mean_direction

## Consulted Papers

- [`amed_solver_2024`](../papers/amed_solver_2024.md)
- [`sa_solver_2025`](../papers/sa_solver_2025.md)

## Session Takeaway


- `AMED-Solver` opens a more interesting deterministic family than the just-closed springboard branch: the paper's real geometric residue is not the learned plugin itself, but the idea that the useful late-step update may be a norm-preserving mean direction inside the recent local drift plane.
- `SA-Solver` is a clear boundary for this repo: stochastic Adams improvements change the sampling problem itself, so they are not the next clean mechanism under the deterministic paper protocol.
- The new orthogonal probe should therefore stay deterministic, keep the `e2379ec` paper base intact everywhere except the single `{steps_left=5}` approach step, and test a tiny AMED-style mean-direction heuristic rather than another state springboard or schedule warp.


## Candidate Card


family=localized_amed_mean_direction
kind=mechanism
external_anchor=Fast ODE-based Sampling for Diffusion Models in Around 5 Steps (Zhou et al., 2024)
borrowed_mechanism=replace the late predictor update direction with a deterministic norm-preserving mean direction built from the local drift plane, approximating the paper's learned mean-direction idea without any trained predictor
synthesis_step=from the exact `e2379ec` paper base, disable the STORK virtual-drift branch on the single `{steps_left=5}` approach step and instead set `predictor_d` to the norm-preserving bisector of `prev_d_cur` and `d_cur`, using the current drift norm and the normalized sum direction; keep the `{4}` midpoint entry step, `{3}` UniPC corrector, and terminal exact-Heun pair unchanged
portability=direct
base_commit=e2379ec
active_nf_range=paper-targeted late full-step regime only; NFE 5/9/11/13 should remain in the usual dormant band because the branch is inactive when `num_steps < 12`
extra_nfe=0
hypothesis=the remaining full-step error may lie in the predictor direction rather than the predictor state; a norm-preserving local mean direction could approximate AMED's learned mean-direction benefit on the one late approach step without learned coefficients or extra evaluations
expected_signature=the proxy frontier should remain in the stable dormant band; if promoted, paper block 0 should stay near or improve on the `e2379ec` base `1.92366`, while a clear proxy loss would reject the mean-direction family quickly
ablation=if this family shows life, compare the same `{5}` placement using the accepted previous slope `prev_d_prime` in the mean-direction span instead of `prev_d_cur`
kill_condition=any low-NFE drift outside the stable band, any instability, or any paper block-0 loss that clearly trails the `e2379ec` base
