# Paper Note: SA-Solver: Stochastic Adams Solver for Fast Sampling of Diffusion Models

paper_id=sa_solver_2025
current_note_from=pass_11
pass_refs=pass_11

## Canonical Note


paper_id=sa_solver_2025
title=SA-Solver: Stochastic Adams Solver for Fast Sampling of Diffusion Models
authors=Shuchen Xue; Mingyang Yi; Weijian Luo; Shifeng Zhang; Jiacheng Sun; Zhenguo Li; Zhi-Ming Ma
venue_or_source=arXiv
year=2025
url=https://arxiv.org/abs/2309.05019
pdf_path=literature/pdfs/sa_solver_2309.05019.pdf
family=variance-controlled stochastic Adams solver for diffusion SDEs
why_relevant=This newly added paper is a useful reject boundary for the current repo because it shows a different route to few-step quality through controlled stochasticity and Adams-style SDE integration rather than through deterministic PF-ODE updates.
core_claim=By solving a family of variance-controlled diffusion SDEs with a stochastic Adams integrator, one can obtain higher-quality or more diverse samples than ODE samplers under suitable NFEs, including strong FID at moderate step counts.
assumptions=Sampling is allowed to inject controlled noise through a time-varying `tau(t)`; the solver is free to operate on the diffusion SDE rather than the deterministic PF-ODE; the model is expressed in data-prediction form for the solver derivation.
complete_sampling_pseudocode=
- Inputs: pretrained diffusion model in data-prediction form; reverse schedule `{t_i}`; noise-scale function `tau(t)` defining the chosen diffusion SDE from the shared marginal family.
- Rewrite the sampling dynamics as a variance-controlled diffusion SDE with drift and diffusion terms determined by `tau(t)`.
- Change variables to the log-SNR coordinate and derive the exponentially weighted stochastic integral.
- Maintain an Adams-style history of previous model evaluations in the transformed coordinates.
- For each reverse step:
- Combine the deterministic Adams predictor term from recent history.
- Add the analytically derived stochastic variance term corresponding to `tau(t)`.
- Advance the sample to the next time point and continue until the final sample is produced.
state_variables_and_history=Current sample; previous transformed drifts or data-prediction evaluations; stochastic noise increments; chosen `tau(t)` schedule; Adams history buffer.
nfe_accounting=The method can be efficient in NFE, but it changes the sampling problem from deterministic PF-ODE integration to stochastic SDE integration with injected noise.
portability=partial
repo_transfer_hypothesis=The only useful lesson here is negative: controlled stochasticity can help at few steps, but this repo's authoritative paper path is deterministic and should not be confounded with an SDE-family change while chasing a simple poster mechanism.
failure_or_reject_boundary=Reject any SA-Solver-like branch that adds stochastic noise, depends on a learned or hand-tuned `tau(t)` noise law, or changes the deterministic paper path into an SDE benchmark.
citation_followups=DPM-Solver++; UniPC; stochastic Adams methods; diffusion SDE versus ODE comparisons
status=ready
