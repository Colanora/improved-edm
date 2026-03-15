# Paper Note: DC-Solver: Improving Predictor-Corrector Diffusion Sampler via Dynamic Compensation

paper_id=dc_solver_2024
current_note_from=pass_00
pass_refs=pass_00

## Canonical Note


paper_id=dc_solver_2024  
title=DC-Solver: Improving Predictor-Corrector Diffusion Sampler via Dynamic Compensation  
authors=Wenliang Zhao; Haolin Wang; Jie Zhou; Jiwen Lu  
venue_or_source=ECCV 2024  
year=2024  
url=https://arxiv.org/abs/2409.03755  
pdf_path=literature/pdfs/dc_solver_2409.03755.pdf  
family=predictor-corrector dynamic compensation / compensated buffer replacement  
why_relevant=This is a recent independently discovered predictor-corrector follow-up from the UniPC line. It is directly relevant to the idea of correcting misalignment between predictor and corrector using a modified buffered score rather than changing the whole solver.  
core_claim=Predictor-corrector samplers suffer from a misalignment between the corrector state and the current score; replacing the current buffered score with a dynamically compensated Lagrange interpolation estimate improves UniPC/DEIS/DPM-Solver++ quality, especially at low NFE and high guidance.  
assumptions=The method assumes an offline search stage with ground-truth trajectories, then a learned or regressed per-step compensation ratio schedule; it targets both unconditional and guided conditional settings.  
complete_sampling_pseudocode=
- Offline search stage:
- For each target step `i`, keep a buffer of the last `K+1` model outputs.
- Define a compensated time `t'_i = rho_i * t_i + (1 - rho_i) * t_{i-1}`.
- Estimate a compensated score at `t'_i` by Lagrange interpolation over buffered past model outputs.
- Replace the current buffered score with this estimate, run one predictor step and one corrector step, and optimize `rho_i` to minimize local error to a ground-truth trajectory.
- Fit a cascade polynomial regressor so `rho_i` can be predicted from CFG, NFE, and step index.
- Sampling stage:
- For each reverse step, if enough history exists, compute the compensated score with the predicted `rho_i` and overwrite the last entry in the buffer.
- Run the base predictor `Pred(x_i^c, Q)` and corrector `Corr(x_{i+1}, eps_theta(x_i, t_i), Q)`.
- Return the final corrected sample.
state_variables_and_history=Corrected current state; predictor state; score buffer `Q`; compensation ratios `rho_i`; interpolated compensated score; optional regressor coefficients.  
nfe_accounting=No extra NFE at sampling time beyond the base predictor-corrector path, but the method depends on offline trajectory search and regression to obtain the compensation schedule.  
portability=partial  
repo_transfer_hypothesis=A hand-crafted, local disagreement-driven compensation factor might approximate the paper's corrected-buffer effect without the offline search. The portable hypothesis is "adjust the late corrector with a deterministic local misalignment signal", not "replicate DC-Solver exactly".  
failure_or_reject_boundary=Reject any candidate that needs searched `rho_i`, saved regressors, guidance-conditioned calibration, or extra assets. Under `program.md`, those are outside the fixed-pretrained `sample.py`-only contract.  
citation_followups=UniPC; DEIS; DPM-Solver++; DPM-Solver-v3  
status=ready
