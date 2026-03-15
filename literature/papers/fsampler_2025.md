# Paper Note: FSampler: Training-Free Acceleration of Diffusion Sampling via Epsilon Extrapolation

paper_id=fsampler_2025
current_note_from=pass_04
pass_refs=pass_03, pass_04

## Canonical Note


paper_id=fsampler_2025
title=FSampler: Training-Free Acceleration of Diffusion Sampling via Epsilon Extrapolation
authors=Michael A. Vladimir
venue_or_source=arXiv
year=2025
url=https://arxiv.org/abs/2511.09180
pdf_path=literature/pdfs/fsampler_2511.09180.pdf
family=epsilon-history extrapolation with explicit model-call skipping
why_relevant=This recent independently discovered paper is useful because it cleanly separates a tempting "training-free acceleration" idea from the repo's fixed-NFE research objective and still offers a lightweight error-signal idea that can be repurposed without skipping calls.
core_claim=One can reduce wall-clock time and NFE by extrapolating the next epsilon from recent real model outputs, validating the prediction with norm/error checks, and substituting the predicted epsilon on selected skip steps while keeping each sampler's update rule unchanged.
assumptions=Sampler framework allows designated skip steps; NFE reduction is allowed; epsilon or denoised predictions are accessible; anchor steps and skip cadence may be changed independently of the underlying solver.
complete_sampling_pseudocode=
- Inputs: sampler state `x_n`, sigma schedule, recent real epsilons, predictor order `h2/h3/h4`, skip policy, optional learning-ratio and gradient-estimation stabilizers.
- On real steps:
- Call the model, compute the true epsilon, append it to epsilon history, and update any EMA-based stabilizer.
- On skip-designated steps:
- Extrapolate `epsilon_hat` from the recent real epsilon history using second-, third-, or fourth-order finite differences.
- Validate `epsilon_hat` for finite values and reasonable norm; cancel the skip if the prediction looks unstable.
- Optionally rescale `epsilon_hat` with a learning-ratio stabilizer and optionally add a local curvature correction.
- Substitute `denoised = x_n + epsilon_hat` and then apply the base sampler's update rule exactly as usual.
- Periodically force anchor steps and protect head/tail windows to prevent long drift.
state_variables_and_history=Current state; sigma schedule; recent real epsilon history; skip cadence or adaptive gate; learning-ratio EMA; optional previous derivative for curvature correction.
nfe_accounting=The central mechanism reduces NFE by skipping model calls, so the method is not a same-budget sampler update.
portability=incompatible
repo_transfer_hypothesis=The portable residue is only the predictor-disagreement idea: use embedded disagreement or extrapolation error as a dormant confidence signal on full-budget steps, not as a skip mechanism.
failure_or_reject_boundary=Reject direct use because the paper's value comes from changing NFE accounting through skipped model calls, which violates the repo's fixed benchmark protocol.
citation_followups=DPM-Solver; DEIS; UniPC; RES multistep samplers; cache-based acceleration papers
status=ready


## Revisit History

### pass_03


paper_id=fsampler_2025
title=FSampler: Training-Free Acceleration of Diffusion Sampling via Epsilon Extrapolation
authors=Michael A. Vladimir
venue_or_source=public method document / ComfyUI whitepaper
year=2025
url=https://arxiv.org/abs/2511.09180
pdf_path=literature/pdfs/fsampler_2511.09180.pdf
family=epsilon-history extrapolation with explicit model-call skipping
why_relevant=This is a recent independently discovered public method document that is not a clean fit for this repo, but it is useful for two reasons: it offers a simple extrapolation-based acceleration story, and it makes the fixed-NFE reject boundary explicit because its core mechanism is step skipping.
core_claim=One can extrapolate the next denoising signal from recent epsilon history using low-order finite-difference formulas, then skip some model calls while keeping the wrapped sampler update rule unchanged; conservative skip cadences preserve perceptual fidelity while reducing wall-clock time.
assumptions=The wrapped sampler is allowed to skip true denoiser evaluations on selected steps; a short epsilon history from real calls is available; guard rails such as protected head/tail windows, anchors, and clamps keep extrapolated skip steps stable.
complete_sampling_pseudocode=
- Inputs: base sampler, noise schedule, skip policy, epsilon history order, optional learning stabilizer and gradient correction.
- For each reverse step:
- If the step is a real-call step, evaluate the model, compute `epsilon`, append it to history, and run the base sampler update unchanged.
- If the step is a skip step and enough history exists, extrapolate `epsilon_hat` from recent real epsilons using linear, Richardson, or cubic finite differences.
- Validate `epsilon_hat` for finiteness and reasonable magnitude; optionally rescale it with an EMA learning ratio and add a small curvature correction.
- Substitute `epsilon_hat` into the wrapped sampler's usual update rule instead of calling the model.
- Periodically force real calls and protect early or late windows from skipping to limit drift.
- Return the final sample and report reduced NFEs.
state_variables_and_history=Current sample and noise level; epsilon history from real calls; skip cadence state; optional EMA learning ratio; optional previous derivative for curvature correction.
nfe_accounting=The method explicitly reduces true NFEs by skipping model calls, so it does not preserve the fixed-budget contract used in this repo.
portability=incompatible
repo_transfer_hypothesis=The only portable lesson is that low-order extrapolation of denoising signals can be stable when aggressively localized and guarded. The faithful FSampler mechanism is still out of scope here because its value comes from skipping calls, not from redistributing a fixed call budget.
failure_or_reject_boundary=Reject direct use because this repo is not evaluating time-saving skip layers; it is comparing fixed-NFE sampler mechanisms under identical call budgets.
citation_followups=DPM-Solver; DPM-Solver++; PFDiff; UniPC; DEIS
status=ready
