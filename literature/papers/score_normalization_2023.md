# Paper Note: Score Normalization for a Faster Diffusion Exponential Integrator Sampler

paper_id=score_normalization_2023
current_note_from=pass_05
pass_refs=pass_05

## Canonical Note


paper_id=score_normalization_2023
title=Score Normalization for a Faster Diffusion Exponential Integrator Sampler
authors=Guoxuan Xia; Duolikun Danier; Ayan Das; Stathi Fotiadis; Farhang Nabiei; Ushnish Sengupta; Alberto Bernacchia
venue_or_source=NeurIPS 2023 Diffusion Workshop / arXiv
year=2023
url=https://arxiv.org/abs/2311.00157
pdf_path=literature/pdfs/score_normalization_2311.00157.pdf
family=score reparameterization / empirical norm normalization for exponential-integrator sampling
why_relevant=This older but newly added source is the cleanest direct anchor for a late-stage scale-calibration family. Its central claim is that low-NFE error is not only directional: the score magnitude itself can become poorly conditioned near the end of sampling, and reparameterizing that magnitude improves fast integration.
core_claim=DEIS improves low-NFE generation by integrating a reparameterized score, but its default `sigma_t` scaling still leaves a sharp late-time change in score magnitude; replacing that with an empirical average-absolute-score normalization computed per timestep improves low-NFE FID consistently.
assumptions=The sampler is based on DEIS or another semi-linear exponential integrator; one can precompute per-timestep average absolute score magnitudes from offline high-NFE runs; the model is a noise-prediction diffusion model or can be converted into an equivalent score form.
complete_sampling_pseudocode=
- Inputs: pretrained diffusion score/noise model `s_theta` or `epsilon_theta`; reverse time grid `{t_i}`; DEIS polynomial order `r`; offline table of average absolute score magnitudes `bar_s(t)`.
- Precompute DEIS coefficients `Psi(t_i, t_j)` and `C_ij` for the chosen schedule and polynomial order, as in vanilla DEIS.
- Build the score reparameterization function `K_t = 1 / bar_s(t)` instead of the default `K_t = sigma_t`.
- During sampling, for each reverse step from `t_i` to `t_{i-1}`:
- Evaluate or reuse the recent score estimates at the required time points.
- Form the normalized integrand samples `-K_{t_{i+j}} s_theta(x_{t_{i+j}}, t_{i+j})`.
- Apply the DEIS time-based Adams-Bashforth update:
- `x_{t_{i-1}} = Psi(t_{i-1}, t_i) x_{t_i} + sum_j C_ij * (-K_{t_{i+j}} s_theta(x_{t_{i+j}}, t_{i+j}))`.
- Continue until the final step and return `x_0`.
- Offline, estimate `bar_s(t)` by running a high-NFE sampler, measuring the average absolute score magnitude at each timestep, and linearly interpolating the resulting table for continuous `t`.
state_variables_and_history=Current sample; current and recent score estimates required by DEIS; DEIS coefficient tables; offline per-timestep score-magnitude table `bar_s(t)`.
nfe_accounting=No extra NFE at inference time relative to the underlying DEIS order, but the method depends on an offline high-NFE statistics pass to estimate `bar_s(t)`.
portability=partial
repo_transfer_hypothesis=The useful portable residue is not the offline DEIS table itself but the idea that late-stage solver error can come from score-magnitude miscalibration. In this repo, a direct translation is to replace the offline table with an online late-history norm reference and localize the effect to the paper-only approach steps before the winning `{4}` midpoint plus `{3}` UniPC tail.
failure_or_reject_boundary=Reject any direct port that requires an offline norm table, a global DEIS solver swap, or low-NFE-path changes. The only in-bounds transfer is a localized online norm calibration inside the existing sampler.
citation_followups=DEIS; gDDIM; Common Diffusion Noise Schedules and Sample Steps Are Flawed
status=ready
