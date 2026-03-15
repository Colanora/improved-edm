# Literature Pass pass_10

pass_id=pass_10
session_date=2026-03-15
working_paper_base=e2379ec
trigger=the accepted-slope STORK consolidation probe also weakened, so the STORK family has exhausted its justified follow-ups and the next branch needs a fresh literature rotation toward a different mechanism family.
paper_refs=pfode_adaptivity_2025, pfode_minimax_2025, pfode_weak_logconcavity_2025
candidate_families=localized_adaptive_predictor_allocation, localized_pfdiff_springboard_predictor

## Consulted Papers

- [`pfode_adaptivity_2025`](../papers/pfode_adaptivity_2025.md)
- [`pfode_minimax_2025`](../papers/pfode_minimax_2025.md)
- [`pfode_weak_logconcavity_2025`](../papers/pfode_weak_logconcavity_2025.md)

## Session Takeaway


- The three fresh PF-ODE theory papers all point to the same practical residue: deterministic samplers benefit from local structure-adaptive behavior, but that behavior should be smooth and local rather than a hard global family swap.
- Together with the existing `sdm_2026` paper entry, the cleanest next family is a per-sample adaptive solver-allocation probe on top of the `e2379ec` paper winner: keep the current STORK virtual predictor available, keep the original extrapolation rule available, and let a local gate decide how much of each to use on the single late `{5}` step.
- This is meaningfully different from the earlier curvature-gated exact-Heun miss: the new family does not promote a whole step to a different solver, it only allocates between two already-tested predictor directions while leaving the downstream midpoint-plus-UniPC tail untouched.


## Candidate Card


family=localized_adaptive_predictor_allocation
kind=mechanism
external_anchor=Formalizing the Sampling Design Space of Diffusion-Based Generative Models via Adaptive Solvers and Wasserstein-Bounded Timesteps (Jo and Choi, 2026); Adaptivity and Convergence of Probability Flow ODEs in Diffusion Generative Models (Tang and Yan, 2025); Minimax Optimality of the Probability Flow ODE for Diffusion Models (Cai and Li, 2025)
borrowed_mechanism=allocate solver behavior smoothly and locally using a per-sample adaptivity signal instead of committing the whole step to one predictor rule
synthesis_step=from the exact `e2379ec` paper base, keep the single `{steps_left=5}` STORK virtual predictor placement but replace the hard choice of the virtual predictor with a smooth per-sample blend between the original extrapolation predictor and the STORK virtual predictor, using the existing `growth_gate` to weight the allocation on that step only; keep the `{4}` midpoint entry step, `{3}` UniPC corrector, and terminal exact-Heun pair unchanged
portability=direct
base_commit=e2379ec
active_nf_range=paper-targeted late full-step regime only; NFE 5/9/11/13 should remain in the usual dormant band because the blend branch is inactive when `num_steps < 12`
extra_nfe=0
hypothesis=the paper-winning STORK predictor may still be over-applied on some samples, while the original extrapolation remains better on others; a smooth local allocation using the existing `growth_gate` could preserve the structural win while reducing the proxy-side overreach that shows up in the same-family misses
expected_signature=the proxy frontier should beat the recent STORK follow-up misses and ideally recover to or improve on the `e2379ec` reference `2.607516`; if promoted, paper block 0 should stay near or improve on `1.92366`
ablation=if this shows life, compare the same allocation using `1 - growth_gate` versus `growth_gate` as the virtual-predictor weight so we can verify the allocation polarity
kill_condition=any low-NFE drift outside the stable band, any instability, or any clear proxy loss that shows the allocation family is weaker than the hard `e2379ec` winner


## Candidate Card


family=localized_pfdiff_springboard_predictor
kind=ablation
external_anchor=PFDiff: Training-Free Acceleration of Diffusion Models Combining Past and Future Scores (Wang et al., 2025); FSampler: Training-Free Acceleration of Diffusion Sampling via Epsilon Extrapolation (Vladimir, 2025)
borrowed_mechanism=keep the same single-step springboard-state family but change which cached past signal defines the springboard, testing raw drift reuse against accepted-slope reuse
synthesis_step=from the exact `e2379ec` base and the just-screened `1082d40` springboard family, keep the same single `{steps_left=5}` springboard placement and replace `prev_d_prime` with the raw previous drift `prev_d_cur` in the predictor-state construction `x_spring = x_hat + alpha * h * prev_d_cur`, leaving the `{4}` midpoint entry step, `{3}` UniPC corrector, and terminal exact-Heun pair unchanged
portability=direct
base_commit=e2379ec
active_nf_range=paper-targeted late full-step regime only; NFE 5/9/11/13 should remain in the usual dormant band because the springboard branch is inactive when `num_steps < 12`
extra_nfe=0
hypothesis=the near-tie miss of `1082d40` suggests that a late springboard state may be directionally sound, but the accepted predictor slope could be slightly over-advanced; using the raw previous drift may yield a cleaner one-step springboard into the winning midpoint-plus-UniPC tail
expected_signature=the proxy frontier should beat `1082d40` and ideally return to or improve on the `e2379ec` proxy reference; if it weakens again, the springboard-state family should be closed and treated as inferior to the STORK virtual-drift family
ablation=if this also weakens, rotate away from springboard-state variants instead of testing more cached-signal choices
kill_condition=any low-NFE drift outside the stable band, any instability, or any paper block-0 signal that would clearly trail the `e2379ec` base
