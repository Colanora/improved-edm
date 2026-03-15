# Literature Pass pass_01

pass_id=pass_01
session_date=2026-03-14
working_paper_base=5e43179
trigger=the post-`5e43179` late-compensation / x_theta / ERA branch has multiple clean misses, so `program.md` requires a fresh literature pass before the next family change.
paper_refs=align_your_steps_2024, optimal_stepsize_2025, geometric_regularity_2025, noise_scheduling_2023
candidate_families=localized_schedule_law

## Consulted Papers

- [`align_your_steps_2024`](../papers/align_your_steps_2024.md)
- [`optimal_stepsize_2025`](../papers/optimal_stepsize_2025.md)
- [`geometric_regularity_2025`](../papers/geometric_regularity_2025.md)
- [`noise_scheduling_2023`](../papers/noise_scheduling_2023.md)

## Session Takeaway


- The new literature pass supports an orthogonal family rotation away from late history compensation and toward a schedule-law probe.
- `Align Your Steps`, `Optimal Stepsize`, and `Geometric Regularity` all say the same high-level thing from different angles: time discretization is a meaningful mechanism, but their exact search procedures are offline and therefore only partial matches for this repo.
- `On the Importance of Noise Scheduling` provides the clean direct hook: changing the inference-time schedule shape or logSNR emphasis alone can matter, even with the same denoiser and same NFE.
- The portable synthesis is therefore a fixed, hand-crafted late full-step schedule warp that is solver-mechanics-neutral and leaves the low-NFE frontier untouched.


## Candidate Card


family=localized_schedule_law
kind=mechanism
external_anchor=Align Your Steps: Optimizing Sampling Schedules in Diffusion Models (Sabour et al., 2024); Geometric Regularity in Deterministic Sampling Dynamics of Diffusion-based Generative Models (Chen et al., 2025); On the Importance of Noise Scheduling for Diffusion Models (Chen, 2023)
borrowed_mechanism=the sampling schedule changes the weighting between the current state and denoising output, and late deterministic trajectories appear to have a distinct turning region that may need different step density than the current hand-crafted late linear branch
synthesis_step=restore the `5e43179` base exactly and leave its predictor/corrector branches untouched, but for `num_steps >= 12` replace the current standard-regime late linear sigma branch with a normalized cosine late-tail law that preserves endpoints and the early branch while smoothly reallocating more resolution to the final standard-regime approach into the `{3,4}` UniPC window and terminal exact-Heun pair
portability=direct
base_commit=5e43179
active_nf_range=paper-targeted late full-step regime only; NFE 5/9/11/13 should stay unchanged because the low-step schedule path remains untouched
extra_nfe=0
hypothesis=a solver-neutral late schedule warp can improve the paper path on top of the `5e43179` mechanism by feeding the existing pre-terminal corrector and terminal exact-Heun pair with a better-conditioned approach trajectory, without reopening the failed late-compensation family
expected_signature=the proxy frontier at NFE 5/9/11/13 stays effectively unchanged; if promoted straight to paper, the full paper row should improve `paper_mean`, not only produce a lucky `fid_min`
ablation=if this wins, compare against the restored `5e43179` base with the same endpoints but the original late linear branch, and then against the opposite smooth warp direction, to isolate whether the gain is specifically from late-tail densification rather than from any smooth schedule change
kill_condition=any unexpected low-NFE drift, any paper row softening versus `5e43179`, or any sign that the schedule warp simply recreates an older scalar schedule-tuning miss instead of delivering a cleaner full-row improvement
