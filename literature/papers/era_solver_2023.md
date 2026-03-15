# Paper Note: ERA-Solver: Error-Robust Adams Solver for Fast Sampling of Diffusion Probabilistic Models

paper_id=era_solver_2023
current_note_from=pass_00
pass_refs=pass_00

## Canonical Note


paper_id=era_solver_2023  
title=ERA-Solver: Error-Robust Adams Solver for Fast Sampling of Diffusion Probabilistic Models  
authors=Shengming Li; Luping Liu; Runnan Li; Xu Tan  
venue_or_source=arXiv 2023  
year=2023  
url=https://arxiv.org/abs/2301.12935  
pdf_path=literature/pdfs/era_solver_2301.12935.pdf  
family=error-robust Adams predictor-corrector / adaptive Lagrange basis selection  
why_relevant=This is the strongest direct new anchor after the failed late-compensation family. The distinctive transferable idea is not just Adams extrapolation itself, but adaptively choosing lower-error history bases instead of trusting one fixed multistep stencil.  
core_claim=ERA-Solver improves fast diffusion sampling by using an implicit Adams predictor-corrector with a Lagrange-interpolation predictor whose bases are adaptively selected to reduce the impact of noisy model-estimation errors; this makes the solver more robust than fixed-coefficient fast samplers.  
assumptions=The sampler has a buffer of previous estimated noises or model outputs; it can rank or select better history bases using an error proxy; predictor-corrector structure is available without extra training.  
complete_sampling_pseudocode=
- Inputs: reverse time grid, current state x_t, buffer of previously estimated noises epsilon_hat at earlier steps, DDIM-like transfer update, chosen predictor-corrector order.
- At each reverse step, maintain a candidate set of previous estimated noises from the buffer.
- Use a Lagrange interpolation predictor instead of a fixed Adams stencil: build the predictor from selected history bases rather than fixed coefficients tied to fixed offsets.
- Rank or choose the history bases expected to have lower estimation error and interpolate the current unobserved term from those bases.
- Use the predicted term inside an implicit-Adams-style corrector / transfer update to produce the next sample state.
- Push the new estimated noise into the buffer and continue.
- Return the final sample after the last reverse step.
- NFE accounting: no extra NFE beyond the predictor-corrector path; robustness comes from adaptive history selection, not extra model calls.
state_variables_and_history=Current sample; buffer of previous estimated noises/model outputs; selected Lagrange bases for the predictor; predictor-corrector state.  
nfe_accounting=Zero extra NFE; the method reuses existing history with adaptive basis selection.  
portability=direct  
repo_transfer_hypothesis=The portable core is a localized adaptive basis choice between competing one-step histories already available in this repo, rather than a full global Lagrange-buffer rewrite. In sample.py that means selecting the more trustworthy previous slope history only on late approach steps before the winning {3,4} UniPC window.  
failure_or_reject_boundary=Reject any version that needs a long history buffer, global stencil rewrite, or changes to the low-NFE path; the useful repo transfer is a very local basis-selection rule.  
citation_followups=PNDM; DPM-Solver++; UniPC; Adams predictor-corrector literature  
status=ready
