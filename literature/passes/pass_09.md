# Literature Pass pass_09

pass_id=pass_09
session_date=2026-03-15
working_paper_base=e2379ec
trigger=the AMED-style mean-direction family missed clearly on the proxy screen, so the next step needs a fresh literature pass before either another orthogonal family or a cleaner consolidation probe on the winning STORK mechanism.
paper_refs=seeds_2023, gddim_2023
candidate_families=localized_stork_virtual_predictor

## Consulted Papers

- [`seeds_2023`](../papers/seeds_2023.md)
- [`gddim_2023`](../papers/gddim_2023.md)

## Session Takeaway


- `SEEDS` and `gDDIM` sharpen the deterministic-vs-stochastic boundary around the current paper winner: both papers explain why there is real few-step headroom in richer solvers, but they also make it clearer that this repo should stay on the deterministic PF-ODE side rather than borrowing stochastic variance terms.
- Together with `STORK`, these papers suggest the current winning mechanism is pointing in the right direction already: the local history vector used to synthesize the late predictor direction matters more than another global schedule or another state springboard.
- The cleanest next consolidation probe is therefore still inside the STORK family: keep the single `{steps_left=5}` virtual-stage construction, but replace the raw previous drift `prev_d_cur` with the accepted previous corrected slope `prev_d_prime` when estimating the virtual predictor direction.


## Candidate Card


family=localized_stork_virtual_predictor
kind=consolidation
external_anchor=STORK: Faster Diffusion And Flow Matching Sampling By Resolving Both Stiffness And Structure-Dependence (Tan et al., 2025); GDDIM: Generalized Denoising Diffusion Implicit Models (Zhang et al., 2023)
borrowed_mechanism=preserve the deterministic virtual-stage predictor idea, but use a more accepted local history vector when estimating the predictor-time slope
synthesis_step=from the exact `e2379ec` paper base, keep the same single `{steps_left=5}` STORK-inspired virtual predictor placement and replace the history difference `(d_cur - prev_d_cur)` with `(d_cur - prev_d_prime)` whenever `prev_d_prime` is available, leaving the `{4}` midpoint entry step, `{3}` UniPC corrector, and terminal exact-Heun pair unchanged
portability=direct
base_commit=e2379ec
active_nf_range=paper-targeted late full-step regime only; NFE 5/9/11/13 should remain in the usual dormant band because the branch is inactive when `num_steps < 12`
extra_nfe=0
hypothesis=the STORK family already won on paper, but the best local history vector may be the accepted previous corrected slope rather than the raw previous drift; using `prev_d_prime` could yield a cleaner virtual-stage direction on the single late approach step without broadening the family
expected_signature=the proxy frontier should stay at least as strong as `e2379ec` and ideally improve on the `2.607516` proxy reference; if promoted, paper block 0 should stay near or improve on `1.92366`
ablation=if this shows life, compare the same `{5}` placement using a gated blend of `prev_d_cur` and `prev_d_prime` rather than a hard swap
kill_condition=any low-NFE drift outside the stable band, any instability, or any proxy loss large enough to show that the accepted-slope history is weaker than the current `e2379ec` history choice
