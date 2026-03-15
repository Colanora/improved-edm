# Paper Note: Align Your Steps: Optimizing Sampling Schedules in Diffusion Models

paper_id=align_your_steps_2024
current_note_from=pass_01
pass_refs=pass_01

## Canonical Note


paper_id=align_your_steps_2024
title=Align Your Steps: Optimizing Sampling Schedules in Diffusion Models
authors=Amirmojtaba Sabour; Sanja Fidler; Karsten Kreis
venue_or_source=ICML 2024 / arXiv
year=2024
url=https://arxiv.org/abs/2404.14507
pdf_path=literature/pdfs/align_your_steps_2404.14507.pdf
family=schedule optimization / solver-aware time discretization
why_relevant=This is the strongest direct literature anchor for treating the sampling schedule itself as a first-class mechanism rather than a frozen backdrop. It is especially relevant now that the active solver family is strong and the next orthogonal move should change the time law instead of adding another late corrector.
core_claim=Sampling schedules are highly suboptimal when left hand-crafted; optimizing the schedule for a fixed solver and pretrained model can substantially improve output quality, with especially large gains in few-step regimes and smaller but still real gains at higher NFE.
assumptions=The method can estimate a KL upper bound between the true learned reverse process and a discretized solver-specific process; it can iterate over intermediate schedule points with Monte Carlo estimates and use early stopping to avoid overfitting path alignment at the expense of final output quality.
complete_sampling_pseudocode=
- Inputs: pretrained diffusion model `D_theta`, chosen solver family, fixed endpoints `t_min, t_max`, initial hand-crafted schedule `t_0 < ... < t_n`, sample subset for Monte Carlo KLUB estimation.
- For each solver interval `[t_{i-1}, t_i]`, define a discretized learned SDE/ODE whose drift freezes the solver's denoiser evaluation pattern on that interval.
- Estimate the per-interval KL upper bound `KLUB(t_{i-1}, t_i)` by drawing noisy states from the forward process and Monte Carlo integrating the squared denoiser mismatch inside the interval.
- Sum these interval costs to obtain the total objective `sum_i KLUB(t_{i-1}, t_i)`.
- Iteratively optimize the intermediate schedule points `t_1 ... t_{n-1}`:
- Select one interior point `t_i`, discretize a neighborhood between `t_{i-1}` and `t_{i+1}`, evaluate the KLUB objective for the candidates, and replace `t_i` with the best candidate.
- Repeat over all interior points for multiple passes, using early stopping based on output-quality validation because excessive KLUB minimization can improve path alignment while worsening final samples.
- Hierarchically subdivide the optimized low-step schedule to higher-step schedules by inserting midpoints in log-sigma space, then fine-tune only the new points while keeping older points fixed.
- For arbitrary target step counts, interpolate the final optimized schedule as a piecewise log-linear sigma curve.
- Run the original solver unchanged on the optimized schedule.
state_variables_and_history=Schedule vector `t_i`; per-interval KLUB values; solver-specific frozen denoiser evaluations inside each interval; validation metric for early stopping.
nfe_accounting=No extra NFE at sampling time once a schedule is chosen, but obtaining the schedule requires an offline Monte Carlo search loop over many candidate schedules.
portability=partial
repo_transfer_hypothesis=The portable lesson is that schedule law remains an underused lever even after the solver mechanics are strong. In this repo the direct transfer is not the offline KLUB search itself, but a simple fixed late-regime schedule warp inspired by the optimized shapes.
failure_or_reject_boundary=Reject any candidate that depends on offline schedule search, manual early-stopping sweeps, or solver-specific KLUB estimation machinery outside `sample.py`. Use this paper as a schedule-law generator, not as a method to reproduce verbatim.
citation_followups=EDM; DPM-Solver; DPM-Solver++; ER-SDE-Solver; learning-to-schedule literature
status=ready
