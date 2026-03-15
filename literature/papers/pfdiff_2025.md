# Paper Note: PFDiff: Training-Free Acceleration of Diffusion Models Combining Past and Future Scores

paper_id=pfdiff_2025
current_note_from=pass_00
pass_refs=pass_00

## Canonical Note


paper_id=pfdiff_2025  
title=PFDiff: Training-Free Acceleration of Diffusion Models Combining Past and Future Scores  
authors=Guangyi Wang; Yuren Cai; Lijiang Li; Wei Peng; Songzhi Su  
venue_or_source=ICLR 2025  
year=2025  
url=https://arxiv.org/abs/2408.08822  
pdf_path=literature/pdfs/pfdiff_2408.08822.pdf  
family=timestep-skipping with springboard / anticipatory update using past and future scores  
why_relevant=This is a recent independently discovered source that explicitly studies how past-score springboards and future-score anticipation interact with ODE discretization error. It is relevant as a boundary case for how much trajectory lookahead is portable into this repo.  
core_claim=A training-free skip strategy can reduce NFE by first using past scores to form a springboard and then using a future-guided anticipatory update, substantially helping first-order ODE samplers and still helping some higher-order baselines under very small NFE.  
assumptions=The method assumes freedom to redefine the internal time grid, group steps into skip patterns, and in the first-order case use a future-guided anticipatory update. For higher-order solvers the final update still uses past scores only.  
complete_sampling_pseudocode=
- Inputs: initial noise `x_T`; target NFE `N`; solver `phi` of order `p`; skip factor `k`; springboard choice `h <= k`; denoiser `eps_theta`.
- Build an internal time grid longer than `N` so one outer iteration covers `k+1` internal substeps.
- Initialize the score buffer `Q` for the first interval and take an initial base update.
- For each outer group of `k+1` internal steps:
- Use past-score-guided solving to move from the current state to a springboard state `x_{t_{i+h}}`.
- Overwrite the score buffer so it now represents the interval from the springboard to the final target of the group.
- If the solver is first-order, take an anticipatory update toward the end of the group using the future-oriented buffer.
- If the solver is higher-order, use the springboard state plus past-score history to reach the final target of the group without new future evaluations.
- Repeat until the final time is reached and return the final sample.
state_variables_and_history=Current state; springboard state; skip factor `k`; springboard offset `h`; score buffer `Q`; internal grouped timestep schedule.  
nfe_accounting=Claimed training-free and practically no extra NFE per output sample, but it does assume a changed internal stepping pattern and grouped updates rather than the repo's fixed Heun-style step contract.  
portability=partial  
repo_transfer_hypothesis=The transferable idea is not the full skip mechanism but the narrower claim that late trajectory error may be improved by a small springboard-like history reuse before the terminal pair. That supports localized late predictor/corrector activity, not a global skip rewrite.  
failure_or_reject_boundary=Reject direct use if it requires a new internal grouped timestep ladder, future-score anticipation, or benefits that appear only on first-order samplers. In this repo, such changes would likely break the stable low-NFE frontier or exceed the clean `sample.py` scope.  
citation_followups=DDIM; DPM-Solver; trajectory geometry papers cited in Section 3; Nesterov-style foresight discussion  
status=ready
