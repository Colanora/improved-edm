# Paper Note: Optimal Stepsize for Diffusion Sampling

paper_id=optimal_stepsize_2025
current_note_from=pass_01
pass_refs=pass_01

## Canonical Note


paper_id=optimal_stepsize_2025
title=Optimal Stepsize for Diffusion Sampling
authors=Jianning Pei; Han Hu; Shuyang Gu
venue_or_source=arXiv
year=2025
url=https://arxiv.org/abs/2503.21774
pdf_path=literature/pdfs/optimal_stepsize_2503.21774.pdf
family=dynamic-programming stepsize distillation
why_relevant=This is a recent independently discovered paper that sharpens the modern schedule-law story. It argues that stepsize selection should be optimized globally against a high-step teacher trajectory, not only locally by heuristic spacing.
core_claim=The stepsize schedule can be derived by a dynamic-programming distillation problem in which an `M`-step student trajectory recursively approximates an `N`-step teacher trajectory; the resulting schedules are robust across architectures, solver orders, and noise schedules.
assumptions=A teacher trajectory with many denoising steps is available; student updates can be compared to teacher states; the objective is recursive in the number of student steps; optional amplitude calibration statistics can be precomputed from teacher/student trajectories.
complete_sampling_pseudocode=
- Inputs: pretrained denoiser `D_theta`, teacher solver with `N` steps, desired student step count `M`, distance metric between teacher and student states.
- Generate the teacher trajectory `x[N], x[N-1], ..., x[0]` with the high-step solver.
- Define the DP subproblem `z[i][j]`: the best `i`-step student approximation to teacher state `x[j]`.
- Initialize `z[0][N]` with the starting noise and all other impossible states with infinity.
- For each student step count `i = 1..M`:
- For each teacher index `j`, evaluate all possible predecessor indices `k > j`.
- Propagate one student step from `z[i-1][k]` to timestep `j` with the chosen solver update `F(z[i-1][k], v_theta, {k, j})`.
- Compute the alignment cost to teacher state `x[j]`, choose the predecessor `k` with minimum cost, store it as `r[i][j]`, and set `z[i][j]` to that propagated state.
- Backtrack the optimal predecessor chain from `z[M][0]` to recover the distilled step schedule.
- Optionally calibrate late-step amplitude by applying a per-step affine rescaling that matches teacher quantile ranges.
- Sample future inputs using the distilled average schedule or the instance-specific schedule.
state_variables_and_history=Teacher trajectory `x[j]`; DP table `z[i][j]`; predecessor indices `r[i][j]`; chosen solver update `F`; optional per-step teacher amplitude statistics.
nfe_accounting=Sampling-time NFE stays fixed once the schedule is distilled, but the method fundamentally depends on an offline teacher trajectory and a dynamic-programming search over candidate student trajectories.
portability=partial
repo_transfer_hypothesis=The direct takeaway for this repo is that the best late schedule is likely to be a globally shaped object rather than a one-point tweak. The portable version is a hand-designed late-regime schedule family that imitates the coarse shape of a distilled optimum without any offline teacher search.
failure_or_reject_boundary=Reject any direct port that needs teacher trajectories, amplitude-calibration statistics, or a DP search stage outside the sampler. Those would violate the frozen `sample.py`-only research contract here.
citation_followups=Align Your Steps; GITS / trajectory-regularity work; LD3; Flow Matching schedule alignment
status=ready
