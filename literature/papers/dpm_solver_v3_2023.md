# Paper Note: DPM-Solver-v3: Improved Diffusion ODE Solver with Empirical Model Statistics

paper_id=dpm_solver_v3_2023
current_note_from=pass_00
pass_refs=pass_00

## Canonical Note


paper_id=dpm_solver_v3_2023  
title=DPM-Solver-v3: Improved Diffusion ODE Solver with Empirical Model Statistics  
authors=Kaiwen Zheng; Cheng Lu; Jianfei Chen; Jun Zhu  
venue_or_source=arXiv 2023  
year=2023  
url=https://arxiv.org/abs/2310.13268  
pdf_path=literature/pdfs/dpm_solver_v3_2310.13268.pdf  
family=empirical-model-statistics predictor-corrector solver  
why_relevant=This is the most relevant modern follow-up in the DPM-Solver line. It makes clear why the full v3 method is outside this repo's clean contract, while still suggesting what part of the idea might be approximated locally without offline assets.  
core_claim=DPM-Solver-v3 improves diffusion ODE sampling by introducing empirical model statistics l, s, b that define a better parameterization and predictor-corrector update; the statistics are estimated on the pretrained model offline and then reused during fast sampling.  
assumptions=The method can estimate empirical model statistics from many samples of the pretrained model; it can precompute integrals involving those statistics; the solver uses a generalized parameterization g_theta and multistep predictor-corrector updates with optional pseudo-order and half-corrector variants.  
complete_sampling_pseudocode=
- Offline EMS stage: sample many states from the pretrained model, estimate coefficient functions l_lambda, s_lambda, b_lambda that minimize first-order discretization error, and precompute the needed integrals over the chosen time grid.
- Sampling stage: rewrite the ODE solution with linear, scaling, and bias coefficients involving the EMS and a transformed model parameterization g_theta.
- For each reverse step, form a local polynomial approximation of g_theta using current and previous cached evaluations.
- Run a multistep predictor to propose the next point, then optionally apply a corrector or pseudo-order corrector using the same cached quantities.
- Reuse the cached model evaluations and EMS integrals at every step until the final sample is produced.
- NFE accounting: no extra NFE beyond the predictor-corrector path at inference time, but the offline EMS estimation is essential to the method.
state_variables_and_history=Current sample; generalized parameterization g_theta; cached previous model outputs; empirical model statistics l,s,b over lambda; predictor-corrector history buffers.  
nfe_accounting=Sampling-time NFE is competitive, but the method depends on an offline EMS estimation pass and precomputed integrals.  
portability=partial  
repo_transfer_hypothesis=A deterministic local surrogate for EMS-like buffer alignment might be portable, but the full method is out of scope because it needs offline statistics and precomputed coefficients tied to the pretrained model.  
failure_or_reject_boundary=Reject any candidate that needs saved EMS tables, offline estimation jobs, or harness changes beyond sample.py; under program.md, those violate the frozen fixed-pretrained contract.  
citation_followups=DPM-Solver++; UniPC; DEIS; exponential Rosenbrock methods  
status=ready
