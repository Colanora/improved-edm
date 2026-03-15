# Paper Note: DualFast: Dual-Speedup Framework for Fast Sampling of Diffusion Models

paper_id=dualfast_2025
current_note_from=pass_00
pass_refs=pass_00

## Canonical Note


paper_id=dualfast_2025  
title=DualFast: Dual-Speedup Framework for Fast Sampling of Diffusion Models  
authors=Hu Yu; Hao Luo; Fan Wang; Feng Zhao  
venue_or_source=arXiv 2025  
year=2025  
url=https://arxiv.org/abs/2506.13058  
pdf_path=literature/pdfs/dualfast_2506.13058.pdf  
family=dual-error compensation with previous high-noise score mixing  
why_relevant=This is a recent independently discovered training-free paper that reframes fast sampling error as approximation error plus discretization error. It offers a simple zero-extra-NFE compensation rule that uses a previous higher-noise score.  
core_claim=Fast samplers optimize discretization error but ignore approximation error from imperfect score prediction. A mixed score `eps_new = (1 + c_t) eps_t - c_t eps_tau` with `tau > t` can reduce total error and plug into DDIM, DPM-Solver, and DPM-Solver++ without extra model evaluations.  
assumptions=The higher-noise score at `tau` is already available from earlier in the reverse trajectory; coefficients `c_t` and source step `tau` are chosen by schedule/analysis; the approximation-error trend decreases with noise level.  
complete_sampling_pseudocode=
- Inputs: base solver update formula expressed through a score-like quantity `D_t`; denoiser `eps_theta`; reverse trajectory states and cached previous scores.
- For each reverse step from high noise to low noise:
- Select a previous higher-noise step `tau > t` whose score is already cached.
- Compute a compensation coefficient `c_t` that grows as the process moves toward lower noise.
- Form the mixed score `eps_new(x_t, t) = (1 + c_t) * eps_theta(x_t, t) - c_t * eps_theta(x_tau, tau)`.
- Substitute `eps_new` into the base solver's first-order term or equivalent `D_t` expression.
- Run the unchanged solver update with this compensated score and continue.
- Return the final sample.
state_variables_and_history=Current state and score; cached previous higher-noise score; compensation coefficient schedule `c_t`; base-solver history terms if the wrapped solver is multistep.  
nfe_accounting=Zero extra NFE if the higher-noise score is reused from history.  
portability=direct  
repo_transfer_hypothesis=A localized late-stage previous-score compensation could be tested in this repo without changing the low-NFE path, but it should be confined to non-terminal standard-regime steps so it does not fight the terminal exact-Heun pair.  
failure_or_reject_boundary=Reject any direct port that globally changes all standard steps or moves the low-NFE frontier. The paper's global compensation schedule is broader than what this repo can currently tolerate.  
citation_followups=DPM-Solver; DPM-Solver++; UniPC; approximation-error analyses cited in Section 3  
status=ready
