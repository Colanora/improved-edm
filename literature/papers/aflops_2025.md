# Paper Note: A-FloPS: Accelerating Diffusion Models via Adaptive Flow Path Sampler

paper_id=aflops_2025
current_note_from=pass_00
pass_refs=pass_00

## Canonical Note


paper_id=aflops_2025  
title=A-FloPS: Accelerating Diffusion Models via Adaptive Flow Path Sampler  
authors=Cheng Jin; Zhenyu Xiao; Yuantao Gu  
venue_or_source=arXiv 2025  
year=2025  
url=https://arxiv.org/abs/2509.00036  
pdf_path=literature/pdfs/aflops_2509.00036.pdf  
family=flow-path reparameterization with adaptive velocity decomposition  
why_relevant=This is a second independently discovered 2025 source that sharpens the reject boundary for global trajectory rewrites. It is useful mainly because it shows why those methods are too broad for this repo even when they are training-free.  
core_claim=Any pretrained diffusion model can be analytically reparameterized into a flow-matching trajectory, and an adaptive decomposition of the resulting velocity field restores the benefits of high-order integration in the few-step regime.  
assumptions=The sampler can globally remap the diffusion trajectory into a flow-matching parameterization, compute the mapped velocity field from the pretrained score model, and adaptively fit a linear drift-plus-residual decomposition during integration.  
complete_sampling_pseudocode=
- Inputs: pretrained score model, diffusion scheduler, target NFE, chosen flow-path ODE integrator.
- Map each diffusion time step to a flow-matching trajectory parameter t and compute the corresponding velocity from the pretrained score model.
- For each reverse step, evaluate the mapped velocity at the current point.
- Estimate an adaptive linear coefficient lambda_t, decompose the velocity into linear drift plus residual, and use the resulting coefficients in a higher-order update formula.
- Advance the flow-path state with the adaptive update and continue until the final sample is reached.
- Return the final sample after the global flow-path integration completes.
- NFE accounting: no extra model evaluations are required, but the entire trajectory parameterization is changed.
state_variables_and_history=Flow-path state x_t; mapped velocity v_t; adaptive linear coefficient lambda_t; residual velocity history; reparameterized time grid.  
nfe_accounting=Training-free and no extra model calls, but relies on a global diffusion-to-flow trajectory rewrite and adaptive velocity decomposition.  
portability=partial  
repo_transfer_hypothesis=The only portable lesson here is that late-stage dynamics may benefit from better-conditioned local trajectories, but the full flow-path rewrite is too broad for the frozen EDM step contract.  
failure_or_reject_boundary=Reject direct use because it changes the global trajectory, time parameterization, and solver semantics rather than expressing one localized sampler mechanism inside the existing EDM loop.  
citation_followups=Flow Matching; DPM-Solver++; UniPC; diffusion-to-flow equivalence work  
status=ready
