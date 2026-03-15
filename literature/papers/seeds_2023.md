# Paper Note: SEEDS: Exponential SDE Solvers for Fast High-Quality Sampling from Diffusion Models

paper_id=seeds_2023
current_note_from=pass_09
pass_refs=pass_09

## Canonical Note


paper_id=seeds_2023
title=SEEDS: Exponential SDE Solvers for Fast High-Quality Sampling from Diffusion Models
authors=Martin Gonzalez; Nelson Fernandez; Thuy Tran; Elies Gherbi; Hatem Hajri; Nader Masmoudi
venue_or_source=arXiv
year=2023
url=https://arxiv.org/abs/2305.14267
pdf_path=literature/pdfs/seeds_2305.14267.pdf
family=stochastic exponential integrator solvers for reverse diffusion SDEs
why_relevant=This newly added paper is a good fresh boundary for the current repo because it is one of the clearest high-quality fast-sampling papers that deliberately keeps stochasticity in the sampler rather than collapsing to a deterministic PF-ODE solver.
core_claim=One can analytically handle the linear part of reverse diffusion SDEs, compute stochastic variance terms in closed form, and build derivative-free stochastic exponential solvers that recover or exceed prior SDE quality with far fewer NFEs.
assumptions=Sampling is allowed to follow the reverse diffusion SDE rather than the deterministic PF-ODE; Gaussian noise increments are injected during inference; the solver may change variables and analytically manipulate stochastic integral terms.
complete_sampling_pseudocode=
- Inputs: pretrained diffusion model `F_theta` or data predictor; reverse time grid `{t_i}` from `T` to `0`; chosen SEEDS order and change-of-variables rule; standard Gaussian noise increments.
- Rewrite the reverse diffusion dynamics in semi-linear SDE form `dx_t = [A(t) x_t + b(t) F_theta(x_t, t)] dt + g(t) dW_t`.
- For each reverse step from `s` to `t`:
- Analytically integrate the linear part through the exponential propagator `Phi_A(t, s)`.
- Change variables so the deterministic neural-network integral becomes an exponentially weighted integral over a transformed coordinate.
- Approximate the transformed deterministic integral with low-order derivative-free terms built from one or more model evaluations depending on the chosen SEEDS order.
- Separately transform the stochastic integral and analytically compute its variance with the stochastic exponential time-differencing construction.
- Sample the corresponding Gaussian increment with that variance and add it to the deterministic update.
- Advance to the next time point and continue until the final sample is produced.
state_variables_and_history=Current sample; transformed exponential propagator factors; current model evaluation and any low-order stage evaluations; analytically computed stochastic variance terms; Gaussian noise increments.
nfe_accounting=The solver can be efficient in NFE, but it changes the sampling path to a stochastic reverse-SDE family with sampled noise increments.
portability=partial
repo_transfer_hypothesis=The only portable residue here is a negative one: exponential-integrator structure remains useful, but once stochastic variance terms are part of the mechanism the paper path is no longer the deterministic PF-ODE target used in this repo.
failure_or_reject_boundary=Reject any SEEDS-like branch that injects stochastic noise, analytically computes SDE variance terms, or otherwise changes the deterministic paper path into a reverse-SDE benchmark.
citation_followups=Exponential integrators; gDDIM; reverse diffusion SDE samplers; SETD methods
status=ready
