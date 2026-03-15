# Paper Note: DPM-Solver: A Fast ODE Solver for Diffusion Probabilistic Model Sampling in Around 10 Steps

paper_id=dpm_solver_2022
current_note_from=pass_04
pass_refs=pass_04

## Canonical Note


paper_id=dpm_solver_2022
title=DPM-Solver: A Fast ODE Solver for Diffusion Probabilistic Model Sampling in Around 10 Steps
authors=Cheng Lu; Yuhao Zhou; Fan Bao; Jianfei Chen; Chongxuan Li; Jun Zhu
venue_or_source=NeurIPS 2022
year=2022
url=https://arxiv.org/abs/2206.00927
pdf_path=literature/pdfs/dpm_solver_2206.00927.pdf
family=dedicated exponential-integrator diffusion ODE solver
why_relevant=This older seminal paper is the clean reference for the "higher-order only where it matters" part of the new SDM pass. It explains how the dedicated diffusion ODE structure changes what a high-order step should look like and helps distinguish principled solver promotion from arbitrary late-step patches.
core_claim=By analytically integrating the linear part of the diffusion ODE and approximating only the exponentially weighted neural-network integral, one can build dedicated first-, second-, and third-order solvers that work in the few-step regime far better than black-box ODE solvers.
assumptions=The diffusion ODE can be expressed with known `alpha_t`, `sigma_t`, and log-SNR `lambda`; the model predicts the noise term or an equivalent representation; one can evaluate the model at the current state and a small number of intermediate states.
complete_sampling_pseudocode=
- Inputs: initial noisy sample `x_T`, reverse timesteps `{t_i}`, corresponding `lambda_i = log(alpha_i / sigma_i)`, trained noise predictor `epsilon_theta`.
- For each step from `t_{i-1}` to `t_i`, write the exact solution as the analytically integrated linear term plus an exponentially weighted integral of `epsilon_theta`.
- First-order version:
- `x_i = alpha_i/alpha_{i-1} * x_{i-1} - sigma_i (exp(h_i)-1) * epsilon_theta(x_{i-1}, t_{i-1})`.
- Second-order version:
- Evaluate an intermediate state at the lambda midpoint `s_i`, run the model there, and use that midpoint prediction in the final update over the full interval.
- Third-order version:
- Evaluate two intermediate states, form finite-difference terms, and use them in the final exponential-integrator update.
- Continue until `t_M = 0`.
state_variables_and_history=Current state; optional midpoint or two-point intermediate states; log-SNR step size `h_i`; model evaluations at current and intermediate states.
nfe_accounting=Zero extra NFE relative to the chosen order: order-1 uses one evaluation, order-2 uses two, order-3 uses three. There is no offline training.
portability=direct
repo_transfer_hypothesis=The full global DPM-Solver family is too disruptive for the current paper winner, but the portable lesson is that exact or dedicated higher-order promotion should be reserved for the genuinely high-curvature late regime rather than sprayed uniformly over the entire trajectory.
failure_or_reject_boundary=Reject a full global swap because earlier localized DPM-Solver++/ERA-style probes already weakened or lost here. The useful role of DPM-Solver in this pass is as the solver-design baseline that SDM's curvature gate decides when to promote toward.
citation_followups=DPM-Solver++; UniPC; SDM adaptive solvers
status=ready
