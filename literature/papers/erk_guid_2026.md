# Paper Note: Error as Signal: Stiffness-Aware Diffusion Sampling via Embedded Runge-Kutta Guidance

paper_id=erk_guid_2026
current_note_from=pass_14
pass_refs=pass_14

## Canonical Note


paper_id=erk_guid_2026
title=Error as Signal: Stiffness-Aware Diffusion Sampling via Embedded Runge-Kutta Guidance
authors=Inho Kong; Sojin Lee; Youngjoon Hong; Hyunwoo J. Kim
venue_or_source=ICLR 2026 / arXiv
year=2026
url=https://arxiv.org/abs/2603.03692
pdf_path=literature/pdfs/erk_guid_2603.03692.pdf
family=stiffness-aware embedded Runge-Kutta guidance for diffusion ODE samplers
why_relevant=This is the cleanest new direct anchor surfaced by the targeted follow-up. Its core mechanism is fully training-free, deterministic, and zero-extra-NFE: use the discrepancy between two embedded solver orders to estimate local stiffness and dominant error direction, then apply a gated correction along that direction.
core_claim=In stiff regions of diffusion ODE sampling, solver-induced local truncation error aligns with the dominant Jacobian eigenvector. A cost-free stiffness estimator and eigenvector proxy derived from the embedded Euler/Heun discrepancy can therefore guide the solver to reduce local error without extra model evaluations.
assumptions=The sampler exposes an embedded Runge-Kutta pair with a lower-order companion and a higher-order update; consecutive step states can be cached; local stiffness can be estimated from solver discrepancies; guidance is only activated when stiffness exceeds a threshold.
complete_sampling_pseudocode=
- Inputs: diffusion drift function `f_theta`; noise schedule `{sigma_i}`; stiffness scale `w_stiff`; confidence threshold `w_con`.
- Initialize sample `x_0` at the starting noise.
- For each step `i`:
- Evaluate the current drift `f_i = f_theta(x_i, sigma_i)` and step size `h = sigma_i - sigma_{i+1}`.
- If a previous embedded pair is available, form
- `Delta_f = f_i - f_euler_prev`,
- `Delta_x = x_i - x_euler_prev`,
- stiffness estimate `rho_hat = ||Delta_f|| / ||Delta_x||`,
- direction estimate `v_hat = Delta_f / ||Delta_f||`.
- Activate guidance only when `rho_hat > w_con`.
- Set `z = w_stiff * h * rho_hat`.
- Define the guidance correction `g_i = beta * z^2 * <f_i, v_hat> * v_hat`.
- Compute the current Euler companion `x_euler_{i+1} = x_i - h * f_i`.
- Evaluate its drift `f_euler_{i+1} = f_theta(x_euler_{i+1}, sigma_{i+1})`.
- Form the Heun update `x_heun_{i+1} = x_i - h * (f_i + f_euler_{i+1}) / 2`.
- Apply the guidance correction `x_{i+1} = x_heun_{i+1} - h * g_i`.
- Cache `(x_euler_{i+1}, f_euler_{i+1})` for the next step and continue.
state_variables_and_history=Current state; current drift; cached Euler companion from the previous embedded pair; cached Euler drift from the previous embedded pair; stiffness estimate `rho_hat`; dominant-direction estimate `v_hat`.
nfe_accounting=Zero extra NFE. The method reuses the already-available lower-order companion and its drift from an embedded RK pair.
portability=direct
repo_transfer_hypothesis=The global guidance framing is broader than this repo needs, but the core residue is directly portable: on a late exact-Heun pair already present in the paper-winning tail, cache the Euler companion and use the next exact-Heun step to apply a stiffness-gated correction along the embedded error direction without changing NFE or the rest of the sampler.
failure_or_reject_boundary=Reject any version that requires conditional guidance branches, extra Jacobian-vector products, adaptive step-size changes, or a global solver rewrite. The in-bounds residue is only the cached embedded-pair stiffness correction itself.
citation_followups=Heun; DPM-Solver; DEIS; stiffness-aware ODE solvers; adaptive step-size control
status=ready
