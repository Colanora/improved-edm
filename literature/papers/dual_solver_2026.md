# Paper Note: Dual-Solver: A Generalized ODE Solver for Diffusion Models with Dual Prediction

paper_id=dual_solver_2026
current_note_from=pass_04
pass_refs=pass_04

## Canonical Note


paper_id=dual_solver_2026
title=Dual-Solver: A Generalized ODE Solver for Diffusion Models with Dual Prediction
authors=Soochul Park; Yeon Ju Lee
venue_or_source=ICLR 2026
year=2026
url=https://arxiv.org/abs/2603.03973
pdf_path=literature/pdfs/dual_solver_2603.03973.pdf
family=learned dual-prediction solver with learned integration domain and residual coefficients
why_relevant=This is a recent independently discovered solver paper that initially looks close to the repo's low-NFE regime, but it is useful mainly as a reject boundary because its gains come from learning per-step coefficients and timesteps.
core_claim=A generalized predictor-corrector solver with learnable parameters controlling prediction type, integration domain, and second-order residual terms can outperform existing few-step solvers when the parameters are optimized end-to-end with a classifier-based objective.
assumptions=The solver parameters and timesteps can be learned offline by backpropagating through the full sampling process using a pretrained classifier or CLIP model; the backbone exposes both `x_theta` and `epsilon_theta` or allows conversion between them.
complete_sampling_pseudocode=
- Inputs: pretrained diffusion backbone, initial noise `x_T`, timesteps `{t_i}`, predictor-corrector solver family with learnable per-step parameters `gamma`, `tau`, `kappa`, and a pretrained classifier or CLIP model for optimization.
- At inference, run a first-order predictor to produce a provisional sample `x'_{t_{i+1}}` from the current state and current model outputs.
- Evaluate the model at the provisional sample and apply a second-order corrector whose coefficients are determined by the learned per-step parameter set.
- Repeat until the final time is reached.
- Offline, optimize all stepwise solver parameters and intermediate timesteps end-to-end so the final decoded image minimizes a classification or CLIP loss, updating the parameters with backpropagation through the sampler.
state_variables_and_history=Current state; predictor and corrector parameter sets for each step; optional converted dual predictions `x_theta` and `epsilon_theta`; learned timesteps; classifier loss targets.
nfe_accounting=Sampling-time NFE can match a standard predictor-corrector sampler, but the method depends on offline learned parameters and learned timesteps.
portability=incompatible
repo_transfer_hypothesis=The only portable lesson is that prediction type and integration domain matter and may vary by step. A faithful Dual-Solver port is out of scope because it requires learned coefficients, learned timesteps, and external optimization machinery.
failure_or_reject_boundary=Reject direct use because the method's value comes from offline parameter learning, which violates the fixed-pretrained, `sample.py`-only contract.
citation_followups=DPM-Solver++; BNS-Solver; DS-Solver; CLIP-based solver learning
status=ready
