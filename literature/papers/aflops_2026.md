# Paper Note: A-FloPS: Accelerating Diffusion Models via Adaptive Flow Path Sampler

paper_id=aflops_2026
current_note_from=pass_08
pass_refs=pass_08

## Canonical Note


paper_id=aflops_2026
title=A-FloPS: Accelerating Diffusion Models via Adaptive Flow Path Sampler
authors=Cheng Jin; Zhenyu Xiao; Yuantao Gu
venue_or_source=AAAI 2026 / arXiv
year=2026
url=https://arxiv.org/abs/2509.00036
pdf_path=literature/pdfs/aflops_2509.00036.pdf
family=flow-path reparameterization with adaptive linear-plus-residual velocity decomposition
why_relevant=This is the cleanest fresh direct source for a small inference-time decomposition mechanism. Its core adaptive step is local, model-agnostic, training-free, and explicitly designed to improve low-NFE high-order integration by peeling away a state-aligned linear drift before extrapolating the residual.
core_claim=Diffusion trajectories can be reparameterized into flow-matching form, and high-order few-step integration improves further when the velocity is decomposed each step into an adaptive linear drift `lambda x` plus a residual with reduced temporal variation; the local closed-form `lambda` estimate is enough to recover substantial low-NFE gains.
assumptions=The sampler can evaluate the current velocity field; consecutive states and velocities are available; one may estimate a piecewise-constant coefficient `lambda^(n)` from local finite differences; no retraining is required.
complete_sampling_pseudocode=
- Inputs: pretrained score or equivalent predictor; number of flow steps `N`; diffusion schedule `{sigma_tau, alpha_bar_tau}`; optional high-order integrator state from the previous step.
- FloPS base trajectory:
- Sample `x_0 ~ N(0, I)` in flow time.
- For each flow step `t_n = n / N`:
- If `t_n` is before the exact diffusion-to-flow mapping becomes valid, reuse the velocity at the earliest valid mapped time `t_min`.
- Otherwise map the flow time `t_n` to the closest diffusion time `tau` satisfying `t_n ≈ 1 / (1 + sigma_tau / alpha_bar_tau)`.
- Convert the pretrained diffusion score or prediction into the corresponding flow velocity `v_{t_n}` at the current state.
- Non-adaptive FloPS update: advance with a simple Euler step `x_{t_{n+1}} = x_{t_n} + v_{t_n} * Delta t`.
- Adaptive A-FloPS update for steps after the first:
- Estimate a local coefficient `lambda^(n)` by minimizing residual variation across consecutive steps:
- `lambda^(n) = <Delta v, Delta x> / ||Delta x||^2`, where `Delta v = v(x_{t_n}, t_n) - v(x_{t_{n-1}}, t_{n-1})` and `Delta x = x_{t_n} - x_{t_{n-1}}`.
- Define the residual velocity `h(x_t, t; lambda) = v(x_t, t) - lambda x_t`.
- Treat `lambda` as piecewise constant over the current interval and integrate the linear term exactly:
- `x_{t_{n+1}} = exp(lambda^(n) Delta t) x_{t_n} + integral exp(lambda^(n) (t_{n+1} - tau)) h(x_tau, tau; lambda^(n)) d tau`.
- Approximate the residual integral with a second-order Taylor expansion using the current residual and a backward finite-difference estimate of `dh/dt`.
- Return the terminal flow state as the generated sample.
state_variables_and_history=Current state; previous state; current velocity; previous velocity; adaptive local coefficient `lambda`; residual velocity `h`; optional high-order finite-difference cache.
nfe_accounting=The adaptive decomposition itself adds no extra model evaluations beyond the wrapped solver because `lambda` is estimated from consecutive already-computed states and velocities.
portability=direct
repo_transfer_hypothesis=The full diffusion-to-flow rewrite is too broad for a single late-step probe, but the adaptive decomposition is directly portable: on the lone `{steps_left=5}` STORK predictor step, estimate a local `lambda` from consecutive states and drifts, subtract the state-aligned linear term `lambda x`, and extrapolate only the residual innovation before reconstructing the predictor drift.
failure_or_reject_boundary=Reject any branch that rewrites the whole repo around a new flow-time parameterization or that requires wholesale scheduler replacement. The direct in-bounds residue is a localized residualized extrapolation inside the existing paper-winning tail.
citation_followups=Flow Matching; DPM-Solver++; UniPC; STORK; rectified flow; Diffusion Meets Flow Matching
status=ready
