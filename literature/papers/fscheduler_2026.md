# Paper Note: F-scheduler: illuminating the free-lunch design space for fast sampling of diffusion models

paper_id=fscheduler_2026
current_note_from=pass_04
pass_refs=pass_04

## Canonical Note


paper_id=fscheduler_2026
title=F-scheduler: illuminating the free-lunch design space for fast sampling of diffusion models
authors=Zilai Li; Lujia Bai
venue_or_source=arXiv
year=2026
url=https://arxiv.org/abs/2510.02390
pdf_path=literature/pdfs/hyperparams_2510.02390.pdf
family=architecture-aware timestep schedule with decoder-noise tolerance and delayed Free-U activation
why_relevant=This recent independently discovered schedule paper initially looks relevant to the repo's schedule-law lane, but its actual mechanism is tightly coupled to latent diffusion decoders and Free-U U-Net modification, making it a useful reject boundary for schedule research here.
core_claim=A customized few-step schedule that stops short of full denoising, optionally inserts an analytical first step, and activates Free-U only at a chosen late stage can outperform stronger baselines in latent diffusion because the beta-VAE decoder can absorb residual noise.
assumptions=Latent diffusion model with a beta-VAE decoder; Free-U or similar skip-connection decorator available inside the U-Net; text-to-image guidance tuning; high-resolution latent pipeline.
complete_sampling_pseudocode=
- Inputs: base ODE solver `F_theta`, total inference step count `N`, Karras-like reference schedule parameters `p1`, `p2`, `stop`, augmentation activation step `t_aug`, optional analytical first-step solver, latent decoder with residual-noise tolerance.
- Compute `sigma_stop` from a Karras-style schedule law using exponent `p2`.
- Build a truncated inference time grid from `t_max` down to `t(sigma_stop)` using exponent `p1` instead of denoising all the way to zero noise.
- Optionally insert an analytical first step between the first two schedule points.
- Run the base ODE solver on the custom schedule.
- Activate Free-U only once the iteration reaches `t_aug`, leaving earlier steps unmodified.
- Decode the residual-noise latent with the beta-VAE decoder, relying on decoder robustness to absorb the remaining small noise.
state_variables_and_history=Current latent state; custom schedule parameters `p1`, `p2`, `stop`; augmentation activation step `t_aug`; optional analytical first-step state; decoder noise floor.
nfe_accounting=The method changes the effective endpoint and time grid and can add an analytical first step, but its main assumptions live outside the sampler update itself.
portability=incompatible
repo_transfer_hypothesis=The only transferable lesson is negative: schedule-law ideas that rely on decoder tolerance, latent-space truncation, or U-Net architecture decorators are not faithful candidates in this fixed-pretrained EDM repo.
failure_or_reject_boundary=Reject direct transfer because this repo has no beta-VAE decoder, no Free-U hook, and already saw a decisive schedule-law paper miss when the mechanism was expressed purely as a schedule warp.
citation_followups=EDM design space; DPM-Solver; Free-U; latent diffusion few-step schedulers
status=ready
