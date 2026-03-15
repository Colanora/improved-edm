# Literature Pass pass_03

pass_id=pass_03
session_date=2026-03-14
working_paper_base=5e43179
trigger=the localized forward-value family also missed badly on paper block 0, so the next rotation must avoid both schedule-only and endpoint-placement families.
paper_refs=rx_dpm_2025, s4s_2025, fsampler_2025, taylorseer_2025
candidate_families=localized_rxdpm_preunipc_block_extrapolation

## Consulted Papers

- [`rx_dpm_2025`](../papers/rx_dpm_2025.md)
- [`s4s_2025`](../papers/s4s_2025.md)
- [`fsampler_2025`](../papers/fsampler_2025.md)
- [`taylorseer_2025`](../papers/taylorseer_2025.md)

## Session Takeaway


- `RX-DPM` is the strongest new direct anchor because it offers a zero-extra-NFE blockwise extrapolation mechanism that is explicitly designed for non-uniform schedules and higher-order solvers.
- `S4S`, `FSampler`, and `TaylorSeer` all sharpen the reject boundary from three different sides: learned coefficients are out of scope, call-skipping layers are out of scope, and internal feature forecasting is out of scope.
- The clean synthesized target is therefore a localized `RX-DPM`-style state extrapolation block that acts only on the two approach steps immediately before the winning `{3,4}` UniPC window, while leaving the rest of `5e43179` untouched.


## Candidate Card


family=localized_rxdpm_preunipc_block_extrapolation
kind=mechanism
external_anchor=Enhanced Diffusion Sampling via Extrapolation with Multiple ODE Solutions (Choi et al., 2025)
borrowed_mechanism=grid-aware Richardson-style extrapolation between a fine two-step solution and a coarse one-step solution over the same late block
synthesis_step=keep the exact `5e43179` sampler everywhere except for one localized two-step block on the late approach steps `{steps_left in 6,5}`; after running those two steps normally, reconstruct a coarse block-end state from the already available start and midpoint drifts, then replace the block-end state with a `p=3` grid-aware extrapolated state before entering the existing `{3,4}` UniPC window
portability=direct
base_commit=2919505
active_nf_range=paper-targeted late full-step regime only; the branch is dormant when `num_steps < 12`, so NFE 5/9/11/13 should remain unchanged
extra_nfe=0
hypothesis=the current `5e43179` paper winner may still carry a two-step approach error into the pre-terminal UniPC window; a localized blockwise extrapolation can reduce that entry error without reopening the failed schedule-only, compensation-only, or forward-value families
expected_signature=the proxy frontier at NFE 5/9/11/13 stays in the current stable band while `fid_N35` improves below `6.7513`; if promoted, paper block 0 should improve over `1.93345` or at least move in the right direction cleanly enough to justify a full row
ablation=if this wins, compare the same block with the extrapolation turned off but the coarse-state buffer still computed, to isolate the gain from the extrapolation combination rather than from incidental refactoring
kill_condition=any `fid_N35` regression, any low-NFE drift outside the current stable band, or any paper block-0 miss that looks like another large translation failure
