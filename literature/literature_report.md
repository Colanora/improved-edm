# Session Literature Report

Session date: 2026-03-14
Working paper base at session start: `8f3ebc2`

This report is the session literature workspace required by `program.md`. The primary purpose is to ground the next `sample.py` candidate in full-text, local-PDF method details rather than memory.

## Paper Entry

paper_id=unipc_2023  
title=UniPC: A Unified Predictor-Corrector Framework for Fast Sampling of Diffusion Models  
authors=Wenliang Zhao; Lujia Bai; Yongming Rao; Jie Zhou; Jiwen Lu  
venue_or_source=arXiv / NeurIPS 2023  
year=2023  
url=https://arxiv.org/abs/2302.04867  
pdf_path=literature/pdfs/unipc_2302.04867.pdf  
family=zero-extra-NFE predictor-corrector / corrector refinement  
why_relevant=This is the cleanest direct anchor for reusing current-step and buffered history to raise effective order without extra model evaluations. It is the closest literature match to this repo's existing corrector-memory line and to the queued localized corrector family.  
core_claim=Given a p-order diffusion ODE solver, UniC-p can use the current predicted point plus the previous p-1 buffered points to lift the corrected solution to order p+1 without adding model evaluations; UniP-p shares the same analytical form and supports arbitrary order.  
assumptions=Diffusion ODE is expressed in half-log-SNR lambda domain; previous model outputs are buffered; the underlying solver already supplies a p-order provisional update; mild smoothness/Lipschitz assumptions are used for the convergence proof.  
complete_sampling_pseudocode=
- Inputs: initial noise `x_T`; reverse timesteps `t_i`; noise predictor `eps_theta`; target order `p`; base p-order solver `Solver-p`; buffer `Q` of previous model outputs.
- Initialize `x_t0 = x_T`, corrected state `x_t0^c = x_T`, and buffer with `eps_theta(x_t0, t_0)`.
- For each reverse step `i = 1..M`:
- Set active order `p_i = min(p, i)` and step size `h_i = lambda(t_i) - lambda(t_{i-1})`.
- Form the first-order base term `x_ti^(1) = alpha_i/alpha_{i-1} * x_{t_{i-1}}^c - sigma_i * (exp(h_i) - 1) * eps_theta(x_{t_{i-1}}, t_{i-1})`.
- Run the chosen p-order predictor `x_ti = Solver-p_i(x_{t_{i-1}}^c, Q)` to get a provisional point.
- Build difference terms against the previous score:
- `D_pi = eps_theta(x_ti, t_i) - eps_theta(x_{t_{i-1}}, t_{i-1})`.
- For older buffered points, set `r_{m-1} = (lambda(t_{i-m}) - lambda(t_{i-1})) / h_i` and `D_{m-1} = eps_theta(x_{t_{i-m}}, t_{i-m}) - eps_theta(x_{t_{i-1}}, t_{i-1})`.
- Compute coefficient vector `a` from the inverse Vandermonde-like system `R^{-1} phi / B(h_i)`.
- Correct the provisional point with the shared analytic form:
- `x_ti^c = x_ti^(1) - sigma_i * B(h_i) * sum_m a_m * D_m / r_m`.
- Push `eps_theta(x_ti, t_i)` into the buffer for the next step.
- Return the final corrected sample.
- UniP-p is the same loop without the current-point correction term; it uses only the previous `p-1` buffered differences and yields a p-order predictor.
state_variables_and_history=Current corrected state `x_ti^c`; provisional predictor state `x_ti`; score buffer `Q`; lambda-domain step size `h_i`; normalized history offsets `r_m`; score differences `D_m`.  
nfe_accounting=No extra NFE relative to a multistep solver that already needs the current-point model output to seed the next buffer. The corrector reuses the current provisional score plus buffered history.  
portability=direct  
repo_transfer_hypothesis=Instead of a globally active UniC correction, a localized late-stage UniPC-style corrector can be activated only on non-terminal standard-regime steps so NFE 5/9/11/13 remain unchanged while NFE 35 and the 18-step paper path improve.  
failure_or_reject_boundary=Reject any translation that perturbs the low-NFE frontier, needs a wider active window than the current late standard regime, or conflicts with the existing terminal exact-Heun pair.  
citation_followups=DPM-Solver; DPM-Solver++; DEIS; PNDM; DPM-Solver-v3  
status=ready

## Paper Entry

paper_id=pndm_2022  
title=Pseudo Numerical Methods for Diffusion Models on Manifolds  
authors=Luping Liu; Yi Ren; Zhijie Lin; Zhou Zhao  
venue_or_source=ICLR 2022  
year=2022  
url=https://arxiv.org/abs/2202.09778  
pdf_path=literature/pdfs/pndm_2202.09778.pdf  
family=pseudo linear multistep / Adams-Bashforth-style predictor reuse  
why_relevant=This is the canonical direct anchor for the repo's current localized multistep predictor family. It explains why reusing score history can help without paying extra per-step NFE once history is bootstrapped.  
core_claim=Diffusion sampling can be treated as a pseudo numerical ODE method on manifolds; after a short Runge-Kutta bootstrap, a pseudo linear multistep update that reuses four past scores gives a better quality/speed tradeoff than DDIM-style first-order transport.  
assumptions=The DDIM/DDPM denoising dynamics are rewritten as a manifold ODE-like update with separate transfer and gradient parts; history reuse is valid after bootstrap; convergence analysis is done for the pseudo transfer form rather than the original Euclidean multistep method.  
complete_sampling_pseudocode=
- Inputs: initial noise `x_T`; reverse step size `delta`; denoiser `eps_theta`; transfer operator `phi`.
- Bootstrap phase for the first three reverse steps:
- Use pseudo Runge-Kutta `PRK` to compute `x_t` and cache the corresponding score `e_t`.
- Main multistep phase for all later steps:
- Evaluate the current score `e_t = eps_theta(x_t, t)`.
- Form the pseudo linear multistep gradient estimate
- `e'_t = (55 * e_t - 59 * e_{t-delta} + 37 * e_{t-2delta} - 9 * e_{t-3delta}) / 24`.
- Apply the DDIM-like transfer operator with the mixed score:
- `x_{t-delta} = phi(x_t, e'_t, t, t-delta)`.
- Shift the history buffer and continue until `x_0`.
- S-PNDM is a shorter-history variant that uses a second-order improved-Euler / two-step multistep combination instead of the four-history update.
state_variables_and_history=Current state `x_t`; current score `e_t`; previous three cached scores; PRK bootstrap states; transfer operator `phi`.  
nfe_accounting=After bootstrap, one model evaluation per reverse step because the multistep formula reuses stored scores. Bootstrap requires extra evaluations for the first few steps, which is why direct whole-trajectory substitution is risky for this repo's low-NFE budgets.  
portability=direct  
repo_transfer_hypothesis=The useful transferable piece is not the full PNDM startup logic but the late localized Adams-Bashforth-style extrapolation on already-stable standard-regime steps. That matches the current repo winner more closely than a full solver swap.  
failure_or_reject_boundary=Reject any implementation that needs altered startup behavior or activates on low-step proxy NFEs, because the paper base already shows that low-NFE translation must remain fixed.  
citation_followups=DDIM; DDPM; neural ODE numerical methods; later DEIS and UniPC multistep samplers  
status=ready

## Paper Entry

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

## Paper Entry

paper_id=dc_solver_2024  
title=DC-Solver: Improving Predictor-Corrector Diffusion Sampler via Dynamic Compensation  
authors=Wenliang Zhao; Haolin Wang; Jie Zhou; Jiwen Lu  
venue_or_source=ECCV 2024  
year=2024  
url=https://arxiv.org/abs/2409.03755  
pdf_path=literature/pdfs/dc_solver_2409.03755.pdf  
family=predictor-corrector dynamic compensation / compensated buffer replacement  
why_relevant=This is a recent independently discovered predictor-corrector follow-up from the UniPC line. It is directly relevant to the idea of correcting misalignment between predictor and corrector using a modified buffered score rather than changing the whole solver.  
core_claim=Predictor-corrector samplers suffer from a misalignment between the corrector state and the current score; replacing the current buffered score with a dynamically compensated Lagrange interpolation estimate improves UniPC/DEIS/DPM-Solver++ quality, especially at low NFE and high guidance.  
assumptions=The method assumes an offline search stage with ground-truth trajectories, then a learned or regressed per-step compensation ratio schedule; it targets both unconditional and guided conditional settings.  
complete_sampling_pseudocode=
- Offline search stage:
- For each target step `i`, keep a buffer of the last `K+1` model outputs.
- Define a compensated time `t'_i = rho_i * t_i + (1 - rho_i) * t_{i-1}`.
- Estimate a compensated score at `t'_i` by Lagrange interpolation over buffered past model outputs.
- Replace the current buffered score with this estimate, run one predictor step and one corrector step, and optimize `rho_i` to minimize local error to a ground-truth trajectory.
- Fit a cascade polynomial regressor so `rho_i` can be predicted from CFG, NFE, and step index.
- Sampling stage:
- For each reverse step, if enough history exists, compute the compensated score with the predicted `rho_i` and overwrite the last entry in the buffer.
- Run the base predictor `Pred(x_i^c, Q)` and corrector `Corr(x_{i+1}, eps_theta(x_i, t_i), Q)`.
- Return the final corrected sample.
state_variables_and_history=Corrected current state; predictor state; score buffer `Q`; compensation ratios `rho_i`; interpolated compensated score; optional regressor coefficients.  
nfe_accounting=No extra NFE at sampling time beyond the base predictor-corrector path, but the method depends on offline trajectory search and regression to obtain the compensation schedule.  
portability=partial  
repo_transfer_hypothesis=A hand-crafted, local disagreement-driven compensation factor might approximate the paper's corrected-buffer effect without the offline search. The portable hypothesis is "adjust the late corrector with a deterministic local misalignment signal", not "replicate DC-Solver exactly".  
failure_or_reject_boundary=Reject any candidate that needs searched `rho_i`, saved regressors, guidance-conditioned calibration, or extra assets. Under `program.md`, those are outside the fixed-pretrained `sample.py`-only contract.  
citation_followups=UniPC; DEIS; DPM-Solver++; DPM-Solver-v3  
status=ready

## Paper Entry

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

## Session Takeaway

- Ready direct anchors for `sample.py`-only work: `UniPC`, `PNDM`, `DualFast`.
- Ready partial anchors that suggest synthesis but not direct reproduction: `PFDiff`, `DC-Solver`.
- Main portability lesson: the repo already rewards mechanisms that are dormant on NFE 5/9/11/13 and only act on late standard-regime, non-terminal steps. The literature backs localized history-based refinement more strongly than global schedule rewrites or learned/offline compensation.
- Synthesized next-family target if the current predictor-scale screen misses: a localized UniPC-style late corrector that reuses buffered history only on the non-terminal standard-regime window immediately before the terminal exact-Heun pair.

## Candidate Card

family=localized_multistep_predictor_scale
kind=tuning
external_anchor=Pseudo Numerical Methods for Diffusion Models on Manifolds (Liu et al., 2022); UniPC (Zhao et al., 2023)
borrowed_mechanism=late Adams-Bashforth-style predictor extrapolation using buffered score history on already-stable non-terminal steps
synthesis_step=one last scale-boundary probe from the `8f3ebc2` paper base: raise the localized predictor extrapolation scale from `0.75` to `1.0` without changing activation timing, terminal handling, or low-NFE behavior
portability=direct
base_commit=8f3ebc2
active_nf_range=late standard/paper regime; NFE 5/9/11/13 should stay unchanged and NFE 35 is the local screen
extra_nfe=0
hypothesis=a slightly stronger late extrapolation sharpens entry into the terminal exact-Heun pair and improves `fid_N35` and paper block 0 without reopening the block-1 softening too much
expected_signature=`fid_N35 < 6.7555` with unchanged NFE 5/9/11/13, and if promoted, a paper block-0 result below `1.95605`
ablation=if this screen misses, restore `8f3ebc2` and rotate to the synthesized localized UniPC-style late-corrector family rather than taking another predictor-only scale step
kill_condition=any low-NFE frontier drift, any `fid_N35` regression versus `8f3ebc2`, or any obvious destabilization of the terminal exact-Heun window

## Candidate Card

family=localized_unipc_preterminal_corrector
kind=mechanism
external_anchor=UniPC (Zhao et al., 2023); DC-Solver (Zhao et al., 2024)
borrowed_mechanism=use the same second model evaluation as a localized corrector that combines the current drift, endpoint drift, and one previous-drift history term
synthesis_step=apply a zero-extra-NFE UniPC-style corrector only on the two pre-terminal standard-regime steps immediately before the existing terminal exact-Heun pair, while restoring the predictor extrapolation scale to the `8f3ebc2` base value of `0.75`
portability=direct
base_commit=8f3ebc2
active_nf_range=paper-targeted late full-step regime only; NFE 5/9/11/13 should remain unchanged because the branch is inactive when `num_steps < 12`
extra_nfe=0
hypothesis=the current base may still be entering the terminal exact-Heun pair with the wrong local curvature on the two preceding steps; replacing only those steps with a localized UniPC-style endpoint/history corrector should improve `fid_N35` without reopening the wider exact-Heun-window failure mode
expected_signature=`fid_N35 < 6.7555` with unchanged NFE 5/9/11/13; if promoted, block 0 should improve beyond `1.95605`
ablation=if this candidate wins, compare the localized corrector against a same-window endpoint-Heun-only version to isolate whether the history term itself matters
kill_condition=any `fid_N35` regression, or any sign that the wider localized corrector behaves like the already-failed widened exact-Heun window rather than a distinct history-aware mechanism

## Candidate Card

family=localized_unipc_preterminal_corrector
kind=ablation
external_anchor=UniPC (Zhao et al., 2023)
borrowed_mechanism=remove the previous-drift history term while keeping the same pre-terminal endpoint evaluation window
synthesis_step=from `5e43179`, keep the `{steps_left in 3,4}` localized branch active but replace the UniPC-style slope with the endpoint-Heun slope already used elsewhere in the sampler
portability=direct
base_commit=5e43179
active_nf_range=paper-targeted late full-step regime only; NFE 5/9/11/13 should remain unchanged because the branch is still inactive when `num_steps < 12`
extra_nfe=0
hypothesis=if the paper win is genuinely coming from the UniPC history term, then preserving the same late window and second evaluation but dropping the history reuse should weaken `fid_N35` relative to `5e43179`
expected_signature=`fid_N35 > 6.7513` with unchanged NFE 5/9/11/13; a large collapse is not required, only a clear weakening versus the winning mechanism
ablation=this is the family ablation required by `program.md`; if it does not weaken, the mechanism story is not yet specific enough
kill_condition=any low-NFE drift, any instability in the `{steps_left in 3,4}` window, or no measurable weakening versus `5e43179`

## Candidate Card

family=localized_unipc_preterminal_corrector
kind=simplification
external_anchor=UniPC (Zhao et al., 2023)
borrowed_mechanism=keep the history-aware corrector but test whether only the final standard-regime step before the terminal exact-Heun pair needs it
synthesis_step=from `5e43179`, shrink `RESEARCH_STANDARD_LOCAL_UNIPC_STEPS_LEFT` from `(3, 4)` to `(3,)` while leaving the localized history-aware slope, predictor scale, and terminal exact-Heun pair unchanged
portability=direct
base_commit=5e43179
active_nf_range=paper-targeted late full-step regime only; NFE 5/9/11/13 should remain unchanged because the branch is still inactive when `num_steps < 12`
extra_nfe=0
hypothesis=the history-aware curvature fix may be concentrated on the last standard-regime step before the terminal exact-Heun pair, so a one-step window could preserve most of the `5e43179` gain while making the mechanism easier to explain
expected_signature=`fid_N35` stays clearly better than the endpoint-Heun-only ablation and remains close enough to `5e43179` to justify the simpler story, with unchanged NFE 5/9/11/13
ablation=if the one-step window softens materially, keep the two-step `5e43179` window as the minimal defensible mechanism
kill_condition=any low-NFE drift or any `fid_N35` result that falls back near the endpoint-Heun-only ablation boundary

## Candidate Card

family=localized_dualfast_preunipc_compensation
kind=mechanism
external_anchor=DualFast: Dual-Speedup Framework for Fast Sampling of Diffusion Models (Yu et al., 2025)
borrowed_mechanism=replace the current score used by the solver with a localized mix of the current score and one cached higher-noise score from the previous step
synthesis_step=keep the `5e43179` two-step `{3,4}` history-aware UniPC window and terminal exact-Heun pair unchanged, but add DualFast-style current-score compensation only on the two earlier approach steps `{5,6}`, reusing the existing late predictor-ramp magnitude as the compensation weight instead of introducing a new tuned schedule
portability=direct
base_commit=5e43179
active_nf_range=late full-step regime; NFE 5/9/11/13 should stay unchanged while NFE 35 and the paper path are active
extra_nfe=0
hypothesis=the current paper winner may still enter the pre-terminal UniPC window with approximation error inherited from the late approach steps; a localized previous-score compensation on `{5,6}` should reduce that entry error and improve `fid_N35` and paper block 0 without disturbing the low-NFE frontier
expected_signature=`fid_N35 < 6.7513` with NFE 5/9/11/13 effectively unchanged; if promoted, paper block 0 should improve beyond `1.93345`
ablation=if this family wins, keep the same `{5,6}` window but remove the higher-noise reuse by zeroing the compensation term, or move the window one step earlier, to verify that the gain is from localized DualFast-style compensation rather than from the mere existence of another late branch
kill_condition=any `fid_N35` regression versus `5e43179`, any low-NFE drift outside the current stable band, or any sign that the added compensation interferes with the winning `{3,4}` UniPC plus terminal exact-Heun structure

## Candidate Card

family=localized_dcsolver_buffer_compensation
kind=mechanism
external_anchor=DC-Solver: Improving Predictor-Corrector Diffusion Sampler via Dynamic Compensation (Zhao et al., 2024)
borrowed_mechanism=replace the buffered previous score used by a predictor-corrector step with a more trajectory-aligned compensated estimate instead of trusting the raw cached score
synthesis_step=restore the `5e43179` winner, keep the `{3,4}` localized UniPC window and terminal exact-Heun pair unchanged, and on the two earlier approach steps `{5,6}` replace `prev_d_cur` inside the late predictor extrapolation with a deterministic blend toward `prev_d_prime`, using the existing predictor-extrapolation magnitude as the local compensation weight
portability=direct
base_commit=5e43179
active_nf_range=late full-step regime; NFE 5/9/11/13 should stay unchanged while NFE 35 and the paper path are active
extra_nfe=0
hypothesis=the failed DualFast screen suggests the approach error is not in the current slope itself but in the buffered history being slightly misaligned with the corrected trajectory; a localized compensated buffer on `{5,6}` should improve entry into the winning pre-terminal UniPC window and beat `fid_N35=6.7513` without disturbing the frontier
expected_signature=`fid_N35 < 6.7513` with NFE 5/9/11/13 effectively unchanged; if promoted, paper block 0 should improve beyond `1.93345`
ablation=if this family wins, keep the same `{5,6}` window but remove the compensated blend back to raw `prev_d_cur`, or move the same compensated-buffer rule into the `{3,4}` window, to test whether the gain is really from localized buffer alignment rather than from another late branch
kill_condition=any `fid_N35` regression versus `5e43179`, any low-NFE drift outside the current stable band, or any paper block-0 loss that mirrors the failed DualFast translation miss

## Candidate Card

family=localized_unipc_preterminal_corrector
kind=simplification
external_anchor=UniPC (Zhao et al., 2023)
borrowed_mechanism=keep the history-aware corrector but test whether only the earlier of the two pre-terminal standard-regime steps carries the transferable gain
synthesis_step=from `5e43179`, shrink `RESEARCH_STANDARD_LOCAL_UNIPC_STEPS_LEFT` from `(3, 4)` to `(4,)` while leaving the localized history-aware slope, predictor scale, and terminal exact-Heun pair unchanged
portability=direct
base_commit=5e43179
active_nf_range=paper-targeted late full-step regime only; NFE 5/9/11/13 should remain unchanged because the branch is still inactive when `num_steps < 12`
extra_nfe=0
hypothesis=the proxy-only success of `{3}` but paper loss on block 0 suggests the paper-side gain may be entering through the earlier pre-terminal correction, not the final one; a `{4}`-only window could therefore be a simpler paper-faithful mechanism
expected_signature=`fid_N35` stays below the endpoint-Heun-only ablation and remains near the two-step base closely enough to justify a paper check, with unchanged NFE 5/9/11/13
ablation=if the `{4}`-only window also misses, keep the two-step `5e43179` window as the minimal paper-qualified story
kill_condition=any low-NFE drift or any `fid_N35` result that falls back near the endpoint-Heun-only ablation boundary

## Paper Entry

paper_id=dpm_solverpp_2022  
title=DPM-Solver++: Fast Solver for Guided Sampling of Diffusion Probabilistic Models  
authors=Cheng Lu; Yuhao Zhou; Fan Bao; Jianfei Chen; Chongxuan Li; Jun Zhu  
venue_or_source=arXiv 2022 / published conference version 2023  
year=2022  
url=https://arxiv.org/abs/2211.01095  
pdf_path=literature/pdfs/dpm_solverpp_2211.01095.pdf  
family=data-prediction exponential-integrator solver / multistep x_theta history reuse  
why_relevant=This is the strongest direct anchor left after the failed late-compensation branch. Its central claim is that high-order diffusion ODE updates become more stable when the history reuse lives in data-prediction space x_theta rather than only in epsilon or drift space, which maps naturally onto this repo's denoised-output interface.  
core_claim=For guided and unconditional diffusion ODE sampling, rewriting the update in x_theta space and then using a multistep second-order solver yields more stable low-NFE behavior than prior epsilon-based high-order solvers; the multistep variant outperforms the singlestep variant when the NFE budget is small.  
assumptions=The sampler can evaluate or reconstruct x_theta from the model output; the diffusion ODE is handled in half-log-SNR lambda coordinates; multistep history from previous model outputs is available; optional thresholding is useful in guided settings but not intrinsic to the solver family.  
complete_sampling_pseudocode=
- Inputs: current state x_s at time s, next time t < s, data-prediction model x_theta(x, time), previous time/state history for multistep updates, lambda-domain step size h = lambda_t - lambda_s.
- Convert the diffusion ODE to the x_theta-based exact-solution form x_t = (sigma_t / sigma_s) * x_s + sigma_t * integral exp(lambda) * x_theta(...) d lambda.
- First-order case: approximate x_theta as constant over the step using x_theta(x_s, s) and compute the closed-form exponential-integrator update.
- Second-order singlestep case: evaluate one intermediate point, estimate the first lambda-derivative of x_theta, and add the corresponding analytic correction term.
- Second-order multistep case DPM-Solver++(2M): reuse the previous step's x_theta history instead of an intermediate evaluation; estimate the first derivative from the current and previous x_theta values; apply the closed-form second-order correction to update x_t without extra NFE.
- Shift the x_theta history buffer and continue to the next reverse step.
- Return the final sample after the last step.
- NFE accounting: after startup, one model evaluation per reverse step; multistep reuse carries the higher-order term.
state_variables_and_history=Current sample x_s; current denoised/data prediction x_theta(x_s, s); previous x_theta history for multistep updates; lambda-domain step size h; optional intermediate point for singlestep variants.  
nfe_accounting=Zero extra NFE for the multistep variant after the history buffer is initialized, because the second-order correction reuses previous x_theta evaluations instead of adding new model calls.  
portability=direct  
repo_transfer_hypothesis=Rather than globally swapping the solver, this repo can try a localized DPM-Solver++-style x_theta multistep switch only on the late non-terminal approach steps right before the winning {3,4} UniPC window, preserving the low-NFE frontier and the current terminal exact-Heun pair.  
failure_or_reject_boundary=Reject any candidate that requires global solver replacement, thresholding-specific gains, or changes to the low-NFE path; the useful transfer is localized x_theta history reuse, not a full solver transplant.  
citation_followups=DPM-Solver; DEIS; UniPC; DPM-Solver-v3  
status=ready

## Paper Entry

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

## Paper Entry

paper_id=tada_2025  
title=TADA: Improved Diffusion Sampling with Training-free Augmented DynAmics  
authors=Tianrong Chen; Huangjie Zheng; David Berthelot; Jiatao Gu; Josh Susskind; Shuangfei Zhai  
venue_or_source=arXiv 2025  
year=2025  
url=https://arxiv.org/abs/2506.21757  
pdf_path=literature/pdfs/tada_2506.21757.pdf  
family=training-free augmented dynamics / momentum diffusion  
why_relevant=This is a recent independently discovered source that usefully defines a reject boundary for this repo. It is attractive at the headline level, but the mechanism depends on augmented state dynamics that are much broader than a clean sampler-only patch here.  
core_claim=By lifting sampling into a higher-dimensional momentum-style state space and reusing a pretrained diffusion model through a special reweighting, TADA obtains stronger few-step generation with an ODE solver and controllable stochastic-like behavior.  
assumptions=Sampling runs in an augmented N-variable state space with a custom transition matrix, reweighting vector r_t, and force term F_theta; the solver operates on the augmented dynamics rather than the original scalar-state diffusion trajectory.  
complete_sampling_pseudocode=
- Inputs: pretrained x_theta model, augmented state dimension N, time grid, ODE solver Psi for the nonlinear term.
- Sample an augmented Gaussian prior x_t0 in the N-variable state space.
- For each reverse step, compute the augmented mean/covariance and the reweighting vector r_t.
- Feed the reweighted projection of the augmented state into the pretrained x_theta model.
- Build a momentum-style force term F_theta from the predicted x_0 and the current augmented derivatives.
- Advance the full augmented state with the controlled transition matrix plus the chosen ODE solver's approximation of the nonlinear term.
- Return the final data prediction reconstructed from the terminal augmented state.
- NFE accounting: the solver can still use one model call per step, but the whole state-space and transition structure are fundamentally changed.
state_variables_and_history=Augmented N-variable state; transition matrix A_t; control vector b_t; reweighting vector r_t; projected network input; optional multistep solver cache.  
nfe_accounting=Training-free in the narrow sense, but not a simple sampler update: the method changes the latent state dimension and trajectory definition.  
portability=incompatible  
repo_transfer_hypothesis=The transferable lesson is only that trajectory-level changes can help in low NFE, but the full augmented-dynamics construction is outside this repo's sample.py-only fixed-state contract.  
failure_or_reject_boundary=Reject direct use because it changes the state dimensionality and sampling dynamics globally, which would no longer be a clean inference-time sampler modification in the existing EDM interface.  
citation_followups=AGM; CLD; DPM-Solver++; UniPC  
status=ready

## Paper Entry

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

## Candidate Card

family=localized_xtheta_multistep_approach
kind=mechanism
external_anchor=DPM-Solver++: Fast Solver for Guided Sampling of Diffusion Probabilistic Models (Lu et al., 2022)
borrowed_mechanism=use multistep history in data-prediction space x_theta instead of relying only on drift-space history
synthesis_step=keep the 5e43179 winner unchanged on the {3,4} localized UniPC window and terminal exact-Heun pair, but on the two earlier approach steps {5,6} replace the current drift-space predictor extrapolation with a localized AB2-style x_theta extrapolation built from the current and previous denoised predictions, then convert it back to drift only for those steps
portability=direct
base_commit=5e43179
active_nf_range=late full-step regime; NFE 5/9/11/13 should remain unchanged while NFE 35 and the paper path are active
extra_nfe=0
hypothesis=data-prediction history may align the approach into the winning pre-terminal UniPC window better than drift-history compensation, so a localized x_theta multistep switch should beat fid_N35=6.7513 without reproducing the paper miss seen from current-slope compensation
expected_signature=`fid_N35 < 6.7513` with the low-step band effectively unchanged; if promoted, paper block 0 should improve beyond `1.93345`
ablation=if this family wins, keep the same {5,6} window but revert to raw drift-space predictor extrapolation, or move the same x_theta multistep rule into the {3,4} window, to test whether the gain truly comes from localized x_theta history reuse
kill_condition=any `fid_N35` regression versus `5e43179`, any low-NFE drift outside the stable band, or any paper block-0 loss that repeats the failed DualFast translation pattern

## Paper Entry

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

## Paper Entry

paper_id=genie_2022  
title=GENIE: Higher-Order Denoising Diffusion Solvers  
authors=Tim Dockhorn; Arash Vahdat; Karsten Kreis  
venue_or_source=arXiv 2022  
year=2022  
url=https://arxiv.org/abs/2210.05475  
pdf_path=literature/pdfs/genie_2210.05475.pdf  
family=higher-order Taylor solver with distilled higher-order score head  
why_relevant=This paper is useful mainly as a reject boundary. It is a clean example of a solver idea that is training-free only in the sampling update but still needs an extra trained head to be practical.  
core_claim=GENIE accelerates diffusion ODE sampling by applying a second-order truncated Taylor method to the DDIM ODE and learning a small additional network head that predicts the required higher-order Jacobian-vector-product terms efficiently during synthesis.  
assumptions=The method can obtain higher-order score terms by automatic differentiation and then distill them into an auxiliary head attached to the score network; practical synthesis depends on that extra learned module.  
complete_sampling_pseudocode=
- Train the base first-order score model as usual.
- Compute the higher-order derivative terms of the DDIM ODE using automatic differentiation / Jacobian-vector products.
- Distill those higher-order terms into a small auxiliary prediction head attached to the score network.
- During sampling, evaluate both the base score model and the auxiliary head at each step.
- Apply the second-order truncated Taylor update using the predicted higher-order derivative term.
- Repeat until the final sample is reached.
state_variables_and_history=Current sample; base score model output; distilled higher-order derivative head output; DDIM ODE step size.  
nfe_accounting=Sampling uses few solver steps, but the approach requires training an additional head and therefore is not a pure sample.py-only modification.  
portability=incompatible  
repo_transfer_hypothesis=The only transferable lesson is that higher-order local curvature matters near the end of the trajectory, but the actual GENIE mechanism is outside this repo because it needs an extra trained module.  
failure_or_reject_boundary=Reject direct use because program.md forbids added trainable parameters and extra model heads.  
citation_followups=DDIM; PNDM; higher-order Itô-Taylor solvers  
status=ready

## Candidate Card

family=localized_era_basis_selection
kind=mechanism
external_anchor=ERA-Solver: Error-Robust Adams Solver for Fast Sampling of Diffusion Probabilistic Models (Li et al., 2023)
borrowed_mechanism=adaptively choose the lower-error history basis for the predictor instead of trusting one fixed Adams-style previous state
synthesis_step=keep the 5e43179 winner unchanged on the {3,4} localized UniPC window and terminal exact-Heun pair, and only on the two earlier approach steps {5,6} choose the predictor history between prev_d_cur and prev_d_prime by whichever is closer to the current drift, then use that selected basis in the existing late extrapolation rule
portability=direct
base_commit=5e43179
active_nf_range=late full-step regime; NFE 5/9/11/13 should remain unchanged while NFE 35 and the paper path are active
extra_nfe=0
hypothesis=the failed compensation variants suggest the issue is not adding another correction term but trusting the wrong late history basis; localized ERA-style basis selection should improve fid_N35 beyond 6.7513 without perturbing the frontier
expected_signature=`fid_N35 < 6.7513` with the low-step band effectively unchanged; if promoted, paper block 0 should improve beyond `1.93345`
ablation=if this family wins, keep the same {5,6} window but force the predictor to always use prev_d_cur or always use prev_d_prime, to verify that the gain comes from basis selection rather than one history being globally better
kill_condition=any `fid_N35` regression versus `5e43179`, any low-NFE drift outside the stable band, or any proxy signature that looks indistinguishable from the failed compensation family

## Candidate Card

family=localized_era_basis_selection
kind=tuning
external_anchor=ERA-Solver: Error-Robust Adams Solver for Fast Sampling of Diffusion Probabilistic Models (Li et al., 2023)
borrowed_mechanism=probe whether one specific lower-error history basis is better than adaptive or fixed-raw history on the late predictor
synthesis_step=from the failed adaptive-basis screen, keep the same {5,6} localized ERA window but force the predictor to always use prev_d_prime there, while leaving the {3,4} UniPC window and terminal exact-Heun pair unchanged
portability=direct
base_commit=5e43179
active_nf_range=late full-step regime; NFE 5/9/11/13 should remain unchanged while NFE 35 and the paper path are active
extra_nfe=0
hypothesis=the adaptive selector may simply be too noisy with only one-step history, while the corrected-history basis prev_d_prime could still be the consistently better late Adams basis and improve fid_N35 beyond 6.7513
expected_signature=`fid_N35 < 6.7513` with the low-step band effectively unchanged; if it loses again, the ERA family should be closed after two misses
ablation=this is the complementary one-sided ablation to the failed adaptive selector; the other endpoint is already represented by the base sampler's default prev_d_cur history
kill_condition=any `fid_N35` regression versus `5e43179`, any low-NFE drift outside the stable band, or a result that lands in the same miss band as the adaptive ERA screen
