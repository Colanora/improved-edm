# Paper Note: On the Importance of Noise Scheduling for Diffusion Models

paper_id=noise_scheduling_2023
current_note_from=pass_01
pass_refs=pass_01

## Canonical Note


paper_id=noise_scheduling_2023
title=On the Importance of Noise Scheduling for Diffusion Models
authors=Ting Chen
venue_or_source=arXiv
year=2023
url=https://arxiv.org/abs/2301.10972
pdf_path=literature/pdfs/noise_scheduling_2301.10972.pdf
family=noise schedule shape / logSNR shift
why_relevant=This paper is not about fast samplers directly, but it provides a simple direct anchor for using monotone schedule shapes and logSNR shifts as meaningful knobs rather than arbitrary cosmetics. It also explicitly states that inference schedules do not need to match training schedules in continuous time.
core_claim=Noise scheduling is crucial; different schedule shapes place emphasis on different noise regions, and simple logSNR shifts or cosine/sigmoid schedule shapes materially change model behavior. During inference, one can discretize time uniformly and choose a desired `gamma(t)` schedule independently.
assumptions=Continuous-time diffusion with a schedule function `gamma(t)` or equivalent logSNR parameterization; optional variance normalization of model inputs; the denoiser can be queried under arbitrary inference-time schedule values.
complete_sampling_pseudocode=
- Inputs: number of sampling steps `S`, continuous schedule function `gamma(t)` or equivalent logSNR law, trained denoiser.
- Sample the initial noisy state from a standard Gaussian.
- For each step `s = 0 .. S-1`:
- Set the current and next times `t_now = 1 - s / S`, `t_next = max(1 - (s+1) / S, 0)`.
- Convert those times through the chosen schedule function `gamma(t)` (or its logSNR equivalent) to determine the noise levels of the current and next states.
- Optionally normalize the current state before the denoiser call.
- Evaluate the denoiser once at the current state and perform the standard DDIM/DDPM-style update toward `t_next` using the scheduled noise levels.
- Repeat until the terminal sample is reached.
state_variables_and_history=Current sample `x_t`; current and next times; schedule function `gamma(t)` or logSNR law; optional input-scaling factor.
nfe_accounting=Zero extra NFE; the schedule only changes which noise levels are visited by the same number of denoiser calls.
portability=direct
repo_transfer_hypothesis=A simple monotone schedule warp in sigma/logSNR space is directly portable to this repo, especially when localized to the full-step standard regime so the low-NFE frontier remains unchanged.
failure_or_reject_boundary=Reject any candidate that implicitly assumes retraining the score model under a new schedule. Only inference-time schedule reshaping is in scope here.
citation_followups=DDPM; RIN; concurrent schedule-parameterization work; Align Your Steps
status=ready
