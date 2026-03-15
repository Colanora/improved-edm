# Paper Note: Are First-Order Diffusion Samplers Really Slower? A Fast Forward-Value Approach

paper_id=forward_value_2026
current_note_from=pass_02
pass_refs=pass_02

## Canonical Note


paper_id=forward_value_2026
title=Are First-Order Diffusion Samplers Really Slower? A Fast Forward-Value Approach
authors=Yuchen Jiao; Na Li; Changxiao Cai; Gen Li
venue_or_source=arXiv
year=2026
url=https://arxiv.org/abs/2512.24927
pdf_path=literature/pdfs/forward_value_2512.24927.pdf
family=forward-value evaluation placement / first-order endpoint sampler
why_relevant=This is a recent independently discovered direct source and the clearest orthogonal mechanism after the schedule-law miss. Its key claim is that evaluation placement can matter independently of solver order, which fits this repo's need for a simple zero-extra-NFE family that does not just add more late history terms.
core_claim=The dominant discretization error is not controlled only by formal solver order; a first-order forward-value update that evaluates the data predictor at a cheap one-step lookahead estimate can outperform or match higher-order samplers at the same NFE.
assumptions=The sampler can build a one-step lookahead estimate of the next state using only information from the current step; the model output can be converted to a data prediction `mu_theta`; time grids and noise schedules are known.
complete_sampling_pseudocode=
- Inputs: pretrained noise predictor `epsilon_theta`, time grid `t_0 > t_1 > ... > t_M`, initial noisy state `x_{t_0}`.
- Define the associated data prediction model `mu_theta(x_t, t) = (x_t - sigma_t * epsilon_theta(x_t, t)) / alpha_t`.
- For each step `i = 1..M`:
- Build a one-step lookahead estimate `hat_x_{t_i}` of the next state using only information up to step `i-1`; the paper suggests a cheap vanilla first-order predictor such as one-step DDIM.
- Evaluate the data predictor at the lookahead state and the forward time endpoint: `mu_theta(hat_x_{t_i}, t_i)`.
- Update the current sample with the forward-value rule
- `x_{t_i} = (sigma_{t_i} / sigma_{t_{i-1}}) * x_{t_{i-1}} - (sigma_{t_i} * alpha_{t_{i-1}} / sigma_{t_{i-1}} - alpha_{t_i}) * mu_theta(hat_x_{t_i}, t_i)`.
- Repeat until `t_M`.
- The lookahead can be replaced by any consistent one-step predictor; the paper also studies a hybrid augmentation that adds this mechanism on top of DPMSolver-2.
state_variables_and_history=Current state `x_{t_i}`; lookahead estimate `hat_x_{t_i}`; time grid; data prediction `mu_theta`; optional hybrid higher-order solver state.
nfe_accounting=One model evaluation per step for the final update plus the same cheap lookahead structure already used by a first-order sampler; in a localized adaptation on top of an existing 2-eval step, it remains zero-extra-NFE because the endpoint evaluation already exists.
portability=direct
repo_transfer_hypothesis=The portable version for this repo is not a full first-order global sampler swap, but a localized forward-value branch on the late approach steps before the winning `{3,4}` UniPC window, using the already available endpoint evaluation to bias the update toward forward-value transport without disturbing the low-NFE path.
failure_or_reject_boundary=Reject any adaptation that globally downgrades the strong `5e43179` solver to a first-order method or that merely recreates the already-failed terminal exactization story. The useful transfer is localized evaluation placement, not replacing the whole sampler.
citation_followups=DDIM; DPMSolver-2; DPMSolver-3; UniPC; convergence-order papers cited in Section 3
status=ready
