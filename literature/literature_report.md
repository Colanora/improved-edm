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

## Session Addendum

Session date: 2026-03-14
Working paper base for this pass: `5e43179`
Reason for new pass: the post-`5e43179` late-compensation / x_theta / ERA branch has multiple clean misses, so `program.md` requires a fresh literature pass before the next family change.

## Paper Entry

paper_id=align_your_steps_2024
title=Align Your Steps: Optimizing Sampling Schedules in Diffusion Models
authors=Amirmojtaba Sabour; Sanja Fidler; Karsten Kreis
venue_or_source=ICML 2024 / arXiv
year=2024
url=https://arxiv.org/abs/2404.14507
pdf_path=literature/pdfs/align_your_steps_2404.14507.pdf
family=schedule optimization / solver-aware time discretization
why_relevant=This is the strongest direct literature anchor for treating the sampling schedule itself as a first-class mechanism rather than a frozen backdrop. It is especially relevant now that the active solver family is strong and the next orthogonal move should change the time law instead of adding another late corrector.
core_claim=Sampling schedules are highly suboptimal when left hand-crafted; optimizing the schedule for a fixed solver and pretrained model can substantially improve output quality, with especially large gains in few-step regimes and smaller but still real gains at higher NFE.
assumptions=The method can estimate a KL upper bound between the true learned reverse process and a discretized solver-specific process; it can iterate over intermediate schedule points with Monte Carlo estimates and use early stopping to avoid overfitting path alignment at the expense of final output quality.
complete_sampling_pseudocode=
- Inputs: pretrained diffusion model `D_theta`, chosen solver family, fixed endpoints `t_min, t_max`, initial hand-crafted schedule `t_0 < ... < t_n`, sample subset for Monte Carlo KLUB estimation.
- For each solver interval `[t_{i-1}, t_i]`, define a discretized learned SDE/ODE whose drift freezes the solver's denoiser evaluation pattern on that interval.
- Estimate the per-interval KL upper bound `KLUB(t_{i-1}, t_i)` by drawing noisy states from the forward process and Monte Carlo integrating the squared denoiser mismatch inside the interval.
- Sum these interval costs to obtain the total objective `sum_i KLUB(t_{i-1}, t_i)`.
- Iteratively optimize the intermediate schedule points `t_1 ... t_{n-1}`:
- Select one interior point `t_i`, discretize a neighborhood between `t_{i-1}` and `t_{i+1}`, evaluate the KLUB objective for the candidates, and replace `t_i` with the best candidate.
- Repeat over all interior points for multiple passes, using early stopping based on output-quality validation because excessive KLUB minimization can improve path alignment while worsening final samples.
- Hierarchically subdivide the optimized low-step schedule to higher-step schedules by inserting midpoints in log-sigma space, then fine-tune only the new points while keeping older points fixed.
- For arbitrary target step counts, interpolate the final optimized schedule as a piecewise log-linear sigma curve.
- Run the original solver unchanged on the optimized schedule.
state_variables_and_history=Schedule vector `t_i`; per-interval KLUB values; solver-specific frozen denoiser evaluations inside each interval; validation metric for early stopping.
nfe_accounting=No extra NFE at sampling time once a schedule is chosen, but obtaining the schedule requires an offline Monte Carlo search loop over many candidate schedules.
portability=partial
repo_transfer_hypothesis=The portable lesson is that schedule law remains an underused lever even after the solver mechanics are strong. In this repo the direct transfer is not the offline KLUB search itself, but a simple fixed late-regime schedule warp inspired by the optimized shapes.
failure_or_reject_boundary=Reject any candidate that depends on offline schedule search, manual early-stopping sweeps, or solver-specific KLUB estimation machinery outside `sample.py`. Use this paper as a schedule-law generator, not as a method to reproduce verbatim.
citation_followups=EDM; DPM-Solver; DPM-Solver++; ER-SDE-Solver; learning-to-schedule literature
status=ready

## Paper Entry

paper_id=optimal_stepsize_2025
title=Optimal Stepsize for Diffusion Sampling
authors=Jianning Pei; Han Hu; Shuyang Gu
venue_or_source=arXiv
year=2025
url=https://arxiv.org/abs/2503.21774
pdf_path=literature/pdfs/optimal_stepsize_2503.21774.pdf
family=dynamic-programming stepsize distillation
why_relevant=This is a recent independently discovered paper that sharpens the modern schedule-law story. It argues that stepsize selection should be optimized globally against a high-step teacher trajectory, not only locally by heuristic spacing.
core_claim=The stepsize schedule can be derived by a dynamic-programming distillation problem in which an `M`-step student trajectory recursively approximates an `N`-step teacher trajectory; the resulting schedules are robust across architectures, solver orders, and noise schedules.
assumptions=A teacher trajectory with many denoising steps is available; student updates can be compared to teacher states; the objective is recursive in the number of student steps; optional amplitude calibration statistics can be precomputed from teacher/student trajectories.
complete_sampling_pseudocode=
- Inputs: pretrained denoiser `D_theta`, teacher solver with `N` steps, desired student step count `M`, distance metric between teacher and student states.
- Generate the teacher trajectory `x[N], x[N-1], ..., x[0]` with the high-step solver.
- Define the DP subproblem `z[i][j]`: the best `i`-step student approximation to teacher state `x[j]`.
- Initialize `z[0][N]` with the starting noise and all other impossible states with infinity.
- For each student step count `i = 1..M`:
- For each teacher index `j`, evaluate all possible predecessor indices `k > j`.
- Propagate one student step from `z[i-1][k]` to timestep `j` with the chosen solver update `F(z[i-1][k], v_theta, {k, j})`.
- Compute the alignment cost to teacher state `x[j]`, choose the predecessor `k` with minimum cost, store it as `r[i][j]`, and set `z[i][j]` to that propagated state.
- Backtrack the optimal predecessor chain from `z[M][0]` to recover the distilled step schedule.
- Optionally calibrate late-step amplitude by applying a per-step affine rescaling that matches teacher quantile ranges.
- Sample future inputs using the distilled average schedule or the instance-specific schedule.
state_variables_and_history=Teacher trajectory `x[j]`; DP table `z[i][j]`; predecessor indices `r[i][j]`; chosen solver update `F`; optional per-step teacher amplitude statistics.
nfe_accounting=Sampling-time NFE stays fixed once the schedule is distilled, but the method fundamentally depends on an offline teacher trajectory and a dynamic-programming search over candidate student trajectories.
portability=partial
repo_transfer_hypothesis=The direct takeaway for this repo is that the best late schedule is likely to be a globally shaped object rather than a one-point tweak. The portable version is a hand-designed late-regime schedule family that imitates the coarse shape of a distilled optimum without any offline teacher search.
failure_or_reject_boundary=Reject any direct port that needs teacher trajectories, amplitude-calibration statistics, or a DP search stage outside the sampler. Those would violate the frozen `sample.py`-only research contract here.
citation_followups=Align Your Steps; GITS / trajectory-regularity work; LD3; Flow Matching schedule alignment
status=ready

## Paper Entry

paper_id=geometric_regularity_2025
title=Geometric Regularity in Deterministic Sampling Dynamics of Diffusion-based Generative Models
authors=Defang Chen; Zhenyu Zhou; Can Wang; Siwei Lyu
venue_or_source=arXiv
year=2025
url=https://arxiv.org/abs/2506.10177
pdf_path=literature/pdfs/geometric_regularity_2506.10177.pdf
family=trajectory-geometry analysis / schedule alignment
why_relevant=This is a recent independently discovered source and the clearest theoretical explanation for why late schedule law might matter on top of an already strong solver. It links sampling schedule choice to the geometry of the denoising trajectory and the convex combination between the current state and denoising output.
core_claim=Deterministic diffusion trajectories lie in a very low-dimensional "boomerang"-shaped subspace; curvature and torsion rise in the late middle of the reverse process and then relax near the end, and this structure can be exploited by a dynamic-programming schedule that better aligns solver time steps with the trajectory geometry.
assumptions=The analysis is done in PF-ODE form, often after converting to a VE-style coordinate system; the denoising output approximates the optimal conditional expectation; trajectory geometry can be studied with high-NFE Euler traces or closed-form KDE arguments.
complete_sampling_pseudocode=
- Inputs: pretrained denoiser `r_theta`, PF-ODE time grid in sigma coordinates, chosen deterministic solver.
- Interpret the solver update as a convex combination between the current state and a generalized denoising output:
- `x_{n} = (sigma_n / sigma_{n+1}) * x_{n+1} + ((sigma_{n+1} - sigma_n) / sigma_{n+1}) * R_theta(x_{n+1})`.
- Observe from high-resolution trajectories that curvature and torsion peak in a late-middle "turning" region before decaying near the terminal denoising regime.
- Use dynamic programming to choose a small number of time steps that align better with that geometric structure, rather than relying on heuristic polynomial spacing.
- Run the same deterministic solver on the geometry-aligned schedule.
- For analysis, project trajectories to the endpoint displacement vector plus top orthogonal principal components to verify the boomerang structure and locate the curvature peak.
state_variables_and_history=Sampling trajectory states; implicit denoising trajectory `r_theta(x_n)`; sigma-ratio schedule; optional projected trajectory bases and curvature/torsion diagnostics.
nfe_accounting=The paper's accelerated sampling method keeps solver NFE fixed once a schedule is chosen, but identifying the geometry-aligned schedule uses offline trajectory analysis or dynamic-programming search.
portability=partial
repo_transfer_hypothesis=The most portable insight is not the paper's DP schedule search but its geometric claim: late full-step dynamics have a turning region before the terminal denoising pair, so a fixed hand-crafted late schedule warp should be judged by whether it gives the pre-terminal correction window better resolution without disturbing the frontier.
failure_or_reject_boundary=Reject any candidate that needs offline trajectory PCA, curvature fitting, or DP search to operate. Keep only the fixed schedule-law hypothesis that can be written directly in `sample.py`.
citation_followups=On the Trajectory Regularity of ODE-based Diffusion Sampling; Align Your Steps; EDM; DPM-Solver; guidance-in-limited-interval work
status=ready

## Paper Entry

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

## Session Takeaway

- The new literature pass supports an orthogonal family rotation away from late history compensation and toward a schedule-law probe.
- `Align Your Steps`, `Optimal Stepsize`, and `Geometric Regularity` all say the same high-level thing from different angles: time discretization is a meaningful mechanism, but their exact search procedures are offline and therefore only partial matches for this repo.
- `On the Importance of Noise Scheduling` provides the clean direct hook: changing the inference-time schedule shape or logSNR emphasis alone can matter, even with the same denoiser and same NFE.
- The portable synthesis is therefore a fixed, hand-crafted late full-step schedule warp that is solver-mechanics-neutral and leaves the low-NFE frontier untouched.

## Candidate Card

family=localized_schedule_law
kind=mechanism
external_anchor=Align Your Steps: Optimizing Sampling Schedules in Diffusion Models (Sabour et al., 2024); Geometric Regularity in Deterministic Sampling Dynamics of Diffusion-based Generative Models (Chen et al., 2025); On the Importance of Noise Scheduling for Diffusion Models (Chen, 2023)
borrowed_mechanism=the sampling schedule changes the weighting between the current state and denoising output, and late deterministic trajectories appear to have a distinct turning region that may need different step density than the current hand-crafted late linear branch
synthesis_step=restore the `5e43179` base exactly and leave its predictor/corrector branches untouched, but for `num_steps >= 12` replace the current standard-regime late linear sigma branch with a normalized cosine late-tail law that preserves endpoints and the early branch while smoothly reallocating more resolution to the final standard-regime approach into the `{3,4}` UniPC window and terminal exact-Heun pair
portability=direct
base_commit=5e43179
active_nf_range=paper-targeted late full-step regime only; NFE 5/9/11/13 should stay unchanged because the low-step schedule path remains untouched
extra_nfe=0
hypothesis=a solver-neutral late schedule warp can improve the paper path on top of the `5e43179` mechanism by feeding the existing pre-terminal corrector and terminal exact-Heun pair with a better-conditioned approach trajectory, without reopening the failed late-compensation family
expected_signature=the proxy frontier at NFE 5/9/11/13 stays effectively unchanged; if promoted straight to paper, the full paper row should improve `paper_mean`, not only produce a lucky `fid_min`
ablation=if this wins, compare against the restored `5e43179` base with the same endpoints but the original late linear branch, and then against the opposite smooth warp direction, to isolate whether the gain is specifically from late-tail densification rather than from any smooth schedule change
kill_condition=any unexpected low-NFE drift, any paper row softening versus `5e43179`, or any sign that the schedule warp simply recreates an older scalar schedule-tuning miss instead of delivering a cleaner full-row improvement

## Session Addendum

Session date: 2026-03-14
Working paper base after schedule-law reject: `5e43179`
Reason for new pass: the localized schedule-law family missed decisively on paper block 0, so the next rotation must come from a different direct mechanism family.

## Paper Entry

paper_id=forward_value_2026
title=Are First-Order Diffusion Samplers Really Slower? A Fast Forward-Value Approach
authors=Yuchen Jiao; Na Li; Changxiao Cai; Gen Li
venue_or_source=arXiv
year=2026
url=https://arxiv.org/abs/2512.24927
pdf_path=literature/pdfs/forward_value_2512.24927.pdf
family=forward-value evaluation placement / first-order endpoint sampler
why_relevant=This is a recent independently discovered direct source and the clearest orthogonal mechanism after the schedule-law miss. Its key claim is that evaluation placement can matter independently of solver order, which fits this repo's need for a simple zero-extra-NFE family that does not just add more late history terms.
core_claim=The dominant discretization error is not controlled only by formal solver order; a first-order forward-value update that evaluates the data predictor at a cheap one-step lookahead estimate can outperform or match higher-order samplers at the same NFE.
assumptions=The sampler can build a one-step lookahead estimate of the next state using only information from the current step; the model output can be converted to a data prediction `mu_theta`; time grids and noise schedules are known.
complete_sampling_pseudocode=
- Inputs: pretrained noise predictor `epsilon_theta`, time grid `t_0 > t_1 > ... > t_M`, initial noisy state `x_{t_0}`.
- Define the associated data prediction model `mu_theta(x_t, t) = (x_t - sigma_t * epsilon_theta(x_t, t)) / alpha_t`.
- For each step `i = 1..M`:
- Build a one-step lookahead estimate `hat_x_{t_i}` of the next state using only information up to step `i-1`; the paper suggests a cheap vanilla first-order predictor such as one-step DDIM.
- Evaluate the data predictor at the lookahead state and the forward time endpoint: `mu_theta(hat_x_{t_i}, t_i)`.
- Update the current sample with the forward-value rule
- `x_{t_i} = (sigma_{t_i} / sigma_{t_{i-1}}) * x_{t_{i-1}} - (sigma_{t_i} * alpha_{t_{i-1}} / sigma_{t_{i-1}} - alpha_{t_i}) * mu_theta(hat_x_{t_i}, t_i)`.
- Repeat until `t_M`.
- The lookahead can be replaced by any consistent one-step predictor; the paper also studies a hybrid augmentation that adds this mechanism on top of DPMSolver-2.
state_variables_and_history=Current state `x_{t_i}`; lookahead estimate `hat_x_{t_i}`; time grid; data prediction `mu_theta`; optional hybrid higher-order solver state.
nfe_accounting=One model evaluation per step for the final update plus the same cheap lookahead structure already used by a first-order sampler; in a localized adaptation on top of an existing 2-eval step, it remains zero-extra-NFE because the endpoint evaluation already exists.
portability=direct
repo_transfer_hypothesis=The portable version for this repo is not a full first-order global sampler swap, but a localized forward-value branch on the late approach steps before the winning `{3,4}` UniPC window, using the already available endpoint evaluation to bias the update toward forward-value transport without disturbing the low-NFE path.
failure_or_reject_boundary=Reject any adaptation that globally downgrades the strong `5e43179` solver to a first-order method or that merely recreates the already-failed terminal exactization story. The useful transfer is localized evaluation placement, not replacing the whole sampler.
citation_followups=DDIM; DPMSolver-2; DPMSolver-3; UniPC; convergence-order papers cited in Section 3
status=ready

## Paper Entry

paper_id=ltc_accel_2025
title=Accelerating Diffusion Sampling via Exploiting Local Transition Coherence
authors=Shangwen Zhu; Han Zhang; Zhantao Yang; Qianyu Peng; Zhao Pu; Huangji Wang; Fan Cheng
venue_or_source=ICCV 2025
year=2025
url=https://arxiv.org/abs/2503.09675
pdf_path=literature/pdfs/ltc_accel_2503.09675.pdf
family=transition-operator reuse / step-skipping acceleration
why_relevant=This is a recent independently discovered training-free paper that initially looks relevant because it exploits local transition structure without network-specific assumptions. It is useful mainly as a reject boundary for this repo's frozen NFE accounting.
core_claim=Adjacent transition operators in diffusion sampling are strongly coherent over a sizable interval, so one can estimate the current transition from neighboring steps and skip explicit denoiser evaluations to accelerate generation.
assumptions=The method identifies an acceleration interval where adjacent transition directions have small angle; it approximates the current transition by a scaled neighboring transition and locally searches a weight parameter `w_g`; practical benefit comes from reducing the number of expensive denoiser evaluations.
complete_sampling_pseudocode=
- Inputs: baseline diffusion sampler with transitions `Delta x_{t+1,t}`, acceleration interval `[a, b]`, denoising progress function `phi(t)`.
- Detect or predefine an interval where the angle between adjacent transition operators is below a threshold.
- For a skipped step `t`, approximate the current transition by reusing the next-step transition:
- `x_t^* = x_{t+1} + w_g * gamma * Delta x_{t+2,t+1}`.
- Set `gamma = (phi(t) - phi(t+1)) / (phi(t+1) - phi(t+2))`.
- Estimate `w_g` by minimizing the discrepancy between the approximated transition and the true transition, with an optional local search across the full acceleration interval.
- Replace true denoiser evaluations inside the acceleration interval with the approximated transitions.
- Outside the interval, run the original sampler unchanged.
state_variables_and_history=Current and adjacent transition operators; acceleration interval; progress ratio `gamma`; locally searched weight `w_g`.
nfe_accounting=The point of the method is to skip denoiser evaluations and gain wall-clock speed, so it changes the effective computation contract even when nominal step counts are reported.
portability=incompatible
repo_transfer_hypothesis=The only portable lesson is that late-step transition directions can be highly redundant, but the actual LTC mechanism is out of scope here because it achieves its benefit by skipping explicit model evaluations instead of spending the fixed NFE budget more intelligently.
failure_or_reject_boundary=Reject direct use because this repo's contract is fixed-NFE sampler research, not step-skipping acceleration. Any faithful LTC adaptation would either change true NFE accounting or require a different benchmark contract.
citation_followups=DeepCache; Align Your Steps; DDIM; DPM-Solver
status=ready

## Session Takeaway

- `Fast Forward-Value` is the most promising new direct family after the schedule-law miss because it changes evaluation placement rather than adding another history buffer or requiring offline search.
- `LTC-Accel` is useful mostly as a reject boundary: it is training-free, but its benefit comes from skipping denoiser evaluations, which is outside this repo's fixed-NFE contract.
- The next clean synthesized target is therefore a localized forward-value branch that changes only how the late approach steps use the already-available endpoint evaluation, while keeping the `5e43179` pre-terminal UniPC window and terminal exact-Heun pair intact.

## Candidate Card

family=localized_forward_value_approach
kind=mechanism
external_anchor=Are First-Order Diffusion Samplers Really Slower? A Fast Forward-Value Approach (Jiao et al., 2026)
borrowed_mechanism=replace a backward-value or symmetric late update with a forward-value update that evaluates the model at a cheap one-step lookahead estimate of the next state
synthesis_step=keep the `5e43179` base unchanged on the `{3,4}` localized UniPC window and terminal exact-Heun pair, but on the two earlier approach steps immediately before that window use the already available endpoint evaluation to take a localized forward-value update instead of the current Heun-style blended slope
portability=direct
base_commit=2510eb1
active_nf_range=paper-targeted late full-step regime only; the low-NFE frontier should remain unchanged because the branch is dormant when `num_steps < 12`
extra_nfe=0
hypothesis=the winning `5e43179` trajectory may still enter the `{3,4}` UniPC window with the wrong signed approach error; a localized forward-value step on the earlier approach interval could improve that entry without another history-compensation branch or a global solver swap
expected_signature=the proxy frontier at NFE 5/9/11/13 stays effectively unchanged; if promoted to paper, block 0 should improve over `1.93345` or at least show a clear same-sign move before spending more paper budget
ablation=if this wins, compare against the same window with the existing Heun-style blended slope and against a pure endpoint-Euler variant with no lookahead reuse, to isolate whether the gain is truly from forward-value placement
kill_condition=any paper block-0 loss that looks like another large translation failure, any unexpected low-NFE drift, or a result that is indistinguishable from the already-rejected late schedule-law family

## Session Addendum

Session date: 2026-03-14
Working paper base after forward-value reject: `5e43179`
Reason for new pass: the localized forward-value family also missed badly on paper block 0, so the next rotation must avoid both schedule-only and endpoint-placement families.

## Paper Entry

paper_id=rx_dpm_2025
title=Enhanced Diffusion Sampling via Extrapolation with Multiple ODE Solutions
authors=Jinyoung Choi; Junoh Kang; Bohyung Han
venue_or_source=ICLR 2025
year=2025
url=https://arxiv.org/abs/2504.01855
pdf_path=literature/pdfs/rx_dpm_2504.01855.pdf
family=grid-aware Richardson extrapolation / blockwise multi-resolution ODE solution mixing
why_relevant=This is a recent independently discovered direct sampler paper and the strongest fresh anchor for a new family here. It is explicitly training-free, keeps NFE fixed, handles non-uniform schedules, and reports that a hybrid `RX+EDM` variant can outperform both plain RX-Euler and Heun by applying extrapolation only on selected late low-noise intervals.
core_claim=Given two numerical solutions over the same interval, one fine `k`-step solution and one coarse single-step solution, a grid-aware Richardson-style extrapolation can cancel the leading truncation term and improve sample quality without extra model evaluations if intermediate predictions are reused from the base solver.
assumptions=The base sampler admits a consistent local truncation order `p`; a coarse estimate over the same interval can be reconstructed from already-computed predictions or reused intermediate evaluations; the score field is smooth enough that the leading truncation term behaves approximately additively across non-uniform substeps.
complete_sampling_pseudocode=
- Inputs: pretrained score model `epsilon_theta`, reverse grid `t_N > ... > t_0`, base ODE solver `Phi`, block size `k`, local solver order `p`, initial noise `x_{t_N}`.
- Partition the trajectory into repeated `k`-step blocks; let the current block start at `t_i` and end at `t_{i-k}`.
- Inside the block, run the original solver normally on each substep to obtain the fine solution `x_hat^(k)_{t_{i-k}}`; store the score evaluations or intermediate predictions that the base solver already computed.
- Let `h = t_i - t_{i-k}` and `lambda_j = (t_{i-j+1} - t_{i-j}) / h` for the `k` substeps in the block.
- Reconstruct a coarse one-step estimate `x_hat^(1)_{t_{i-k}} = Phi(x_{t_i}, t_i, t_{i-k})` over the same full interval, reusing the stored predictions so no extra NFE is spent.
- Form the grid-aware extrapolated state
- `x_tilde^(k)_{t_{i-k}} = (x_hat^(k)_{t_{i-k}} - (sum_j lambda_j^p) * x_hat^(1)_{t_{i-k}}) / (1 - sum_j lambda_j^p)`.
- Replace the block-end state with `x_tilde^(k)_{t_{i-k}}` and continue the next block from that corrected state.
- For leftover steps that do not fill a full block, either shorten `k` or skip extrapolation.
- For higher-order Runge-Kutta-like solvers, reuse the already-computed intermediate-stage evaluations to build the coarse estimate; for multistep solvers, reuse buffered past evaluations.
state_variables_and_history=Current state at the start of a block; fine block-end state; reconstructed coarse block-end state; blockwise substep ratios `lambda_j`; solver order `p`; any intermediate stage evaluations or stored past drifts required by the base solver.
nfe_accounting=Zero extra NFE when the coarse estimate reuses intermediate evaluations already computed for the fine block; the extra work is only storing a few states and taking a linear combination at block end.
portability=direct
repo_transfer_hypothesis=The portable version for this repo is a localized two-step extrapolation block immediately before the winning `{3,4}` UniPC window: keep the existing fine trajectory for the two approach steps, reconstruct a coarse block-end state from the already available start and midpoint drifts, then feed the extrapolated state into the unchanged UniPC plus terminal exact-Heun tail.
failure_or_reject_boundary=Reject any translation that broadens into a global schedule rewrite or needs a new extra evaluation to build the coarse estimate. The useful transfer is localized blockwise state extrapolation, not replacing the whole sampler with RX-Euler.
citation_followups=EDM; DDIM; PNDM; DPM-Solver; IIA; LA-DPM
status=ready

## Paper Entry

paper_id=s4s_2025
title=S4S: Solving for a Diffusion Model Solver
authors=Eric Frankel; Sitan Chen; Jerry Li; Pang Wei Koh; Lillian J. Ratliff; Sewoong Oh
venue_or_source=arXiv
year=2025
url=https://arxiv.org/abs/2502.17423
pdf_path=literature/pdfs/s4s_2502.17423.pdf
family=learned solver coefficients and learned discretization schedules
why_relevant=This is a recent independently discovered solver-design paper that is useful as a sharp reject boundary. It directly targets the same low-NFE sampler space, but its gains come from offline optimization of time-dependent coefficients and optionally schedules.
core_claim=Few-NFE diffusion sampling is better treated as a global solver-design problem than a classical local truncation problem; learning solver coefficients, and optionally discretization steps, against a strong teacher yields uniformly better few-step samplers than fixed analytic coefficients.
assumptions=A strong teacher solver is available; one can optimize solver coefficients and possibly schedule parameters offline using generated teacher samples and backpropagation; inference uses the learned coefficients without retraining the denoiser itself.
complete_sampling_pseudocode=
- Inputs: pretrained score model, fixed solver family parameterization `Psi_phi` with learnable time-dependent coefficients `phi`, optional learnable schedule parameters `Xi`, teacher solver `Psi_*`, distance metric `d`, noise radius `r`.
- Sample many initial noise latents `x_T`; for each one, precompute the teacher output `Psi_*(x_T)`.
- Optimize the student solver by minimizing `d(Psi_phi(x'_T), Psi_*(x_T))` subject to `x'_T` staying in a small ball around `x_T`; update both `phi` and the relaxed latent `x'_T` with projected SGD.
- When learning only coefficients, keep the time grid fixed and learn per-step solver weights for LMS, single-step, or predictor-corrector formulas.
- When learning schedules too, alternate between updating schedule parameters `Xi` and coefficient parameters `phi` while repeatedly re-running the student solver on the teacher dataset.
- At inference time, sample with the learned coefficients and schedule exactly as a normal diffusion sampler, with no extra train-time machinery.
state_variables_and_history=Learnable solver coefficients; optional learnable discretization parameters; relaxed input latents used during offline optimization; teacher outputs.
nfe_accounting=Sampling-time NFE is unchanged once the solver is learned, but the method fundamentally depends on offline optimization and stored teacher trajectories.
portability=incompatible
repo_transfer_hypothesis=The transferable lesson is only that late-step coefficients may want to be time-dependent and solver-family-specific. A faithful S4S reproduction is out of scope because this repo forbids offline optimization, learned coefficients, and new assets.
failure_or_reject_boundary=Reject direct use because the method needs offline optimization over solver coefficients and optionally schedules. Any faithful port would violate the fixed-pretrained, `sample.py`-only contract even though inference-time NFE stays fixed.
citation_followups=LD3; iPNDM; UniPC; DPM-Solver-v3; BNS; AMED-Plugin
status=ready

## Paper Entry

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

## Paper Entry

paper_id=taylorseer_2025
title=From Reusing to Forecasting: Accelerating Diffusion Models with TaylorSeers
authors=Jiacheng Liu; Chang Zou; Yuanhuiyi Lyu; Junjie Chen; Linfeng Zhang
venue_or_source=arXiv
year=2025
url=https://arxiv.org/abs/2503.06923
pdf_path=literature/pdfs/taylorseer_2503.06923.pdf
family=feature-cache forecasting inside diffusion transformers
why_relevant=This is a recent independently discovered acceleration paper that is useful mainly as a reject boundary. Its "forecast rather than reuse" idea rhymes with extrapolation, but the actual mechanism lives inside the model's hidden-feature cache rather than at the sampler update level.
core_claim=Instead of reusing cached hidden features from earlier timesteps, predict future transformer features with Taylor-series finite differences; this preserves quality at much higher acceleration ratios than naive cache reuse.
assumptions=The diffusion model exposes internal layer features across timesteps; those features evolve smoothly enough for finite-difference forecasting; inference can skip large parts of transformer computation by substituting forecast features.
complete_sampling_pseudocode=
- Inputs: diffusion transformer with cacheable block features, cache interval `N`, Taylor order `m`.
- At fully computed timesteps, cache each layer feature and its finite differences up to order `m`.
- For skipped intermediate timesteps, predict each feature with the Taylor expansion `F_pred(t-k) = F(t) + sum_i Delta^i F(t) * (-k)^i / (i! * N^i)`.
- Feed the forecast features through the remaining computation instead of recomputing the expensive layers.
- Periodically refresh the cache with a full model evaluation and update the finite-difference stack.
- Continue sampling with the accelerated internal model execution.
state_variables_and_history=Per-layer cached features; finite-difference feature stack; cache interval; Taylor order; skipped-step counters.
nfe_accounting=The paper accelerates inference by reusing or forecasting internal features and skipping substantial model computation, not by changing a fixed sampler mechanism under an identical denoiser-call contract.
portability=incompatible
repo_transfer_hypothesis=The portable lesson is only conceptual: forecasting can outperform raw reuse when a state trajectory is smooth. The actual TaylorSeer mechanism is incompatible because this repo exposes only the sampler surface, not model internals or feature caches.
failure_or_reject_boundary=Reject direct use because it requires instrumenting hidden transformer features and caching internal activations, which is far outside the `sample.py`-only contract.
citation_followups=FORA; ToCa; TeaCache; DiT acceleration papers
status=ready

## Session Takeaway

- `RX-DPM` is the strongest new direct anchor because it offers a zero-extra-NFE blockwise extrapolation mechanism that is explicitly designed for non-uniform schedules and higher-order solvers.
- `S4S`, `FSampler`, and `TaylorSeer` all sharpen the reject boundary from three different sides: learned coefficients are out of scope, call-skipping layers are out of scope, and internal feature forecasting is out of scope.
- The clean synthesized target is therefore a localized `RX-DPM`-style state extrapolation block that acts only on the two approach steps immediately before the winning `{3,4}` UniPC window, while leaving the rest of `5e43179` untouched.

## Candidate Card

family=localized_rxdpm_preunipc_block_extrapolation
kind=mechanism
external_anchor=Enhanced Diffusion Sampling via Extrapolation with Multiple ODE Solutions (Choi et al., 2025)
borrowed_mechanism=grid-aware Richardson-style extrapolation between a fine two-step solution and a coarse one-step solution over the same late block
synthesis_step=keep the exact `5e43179` sampler everywhere except for one localized two-step block on the late approach steps `{steps_left in 6,5}`; after running those two steps normally, reconstruct a coarse block-end state from the already available start and midpoint drifts, then replace the block-end state with a `p=3` grid-aware extrapolated state before entering the existing `{3,4}` UniPC window
portability=direct
base_commit=2919505
active_nf_range=paper-targeted late full-step regime only; the branch is dormant when `num_steps < 12`, so NFE 5/9/11/13 should remain unchanged
extra_nfe=0
hypothesis=the current `5e43179` paper winner may still carry a two-step approach error into the pre-terminal UniPC window; a localized blockwise extrapolation can reduce that entry error without reopening the failed schedule-only, compensation-only, or forward-value families
expected_signature=the proxy frontier at NFE 5/9/11/13 stays in the current stable band while `fid_N35` improves below `6.7513`; if promoted, paper block 0 should improve over `1.93345` or at least move in the right direction cleanly enough to justify a full row
ablation=if this wins, compare the same block with the extrapolation turned off but the coarse-state buffer still computed, to isolate the gain from the extrapolation combination rather than from incidental refactoring
kill_condition=any `fid_N35` regression, any low-NFE drift outside the current stable band, or any paper block-0 miss that looks like another large translation failure

## Session Addendum

Session date: 2026-03-14
Working paper base after RX-DPM reject: `5e43179`
Reason for new pass: the localized RX-DPM approach also failed on paper block 0, so the next rotation must avoid schedule-only, endpoint-placement, and block-extrapolation mechanisms.

## Paper Entry

paper_id=sdm_2026
title=Formalizing the Sampling Design Space of Diffusion-Based Generative Models via Adaptive Solvers and Wasserstein-Bounded Timesteps
authors=Sangwoo Jo; Sungjoon Choi
venue_or_source=arXiv
year=2026
url=https://arxiv.org/abs/2602.12624
pdf_path=literature/pdfs/sdm_2602.12624.pdf
family=adaptive solver allocation and adaptive timestep scheduling
why_relevant=This is a recent independently discovered direct paper and the most relevant new family after the RX miss. Its direct sampler-side contribution is a cache-based curvature proxy that decides when low-order versus higher-order updates are needed, without adding model evaluations or training.
core_claim=Diffusion trajectories are nearly linear in the high-noise regime and sharply more curved near the data manifold; one can therefore improve the quality/efficiency tradeoff by using cached relative curvature to adapt the solver order and by reallocating timestep density with a Wasserstein-bounded schedule.
assumptions=The vector field can be evaluated at the current step and cached from the previous one; local stiffness is well approximated by the discrete relative-curvature proxy; adaptive schedules can be precomputed or searched offline for a target NFE budget.
complete_sampling_pseudocode=
- Inputs: pretrained diffusion model, reverse timesteps `t_0 > ... > t_N`, solver family with Euler and Heun updates, optional adaptive schedule parameters.
- For each step, compute the current vector field `v_i` at `(x_i, t_i)` and reuse the previous cached field `v_{i-1}`.
- Form the cache-based relative-curvature proxy `kappa_hat(i) = ||v_i - v_{i-1}|| / (Delta t_{i-1} ||v_{i-1}||)`.
- Convert this curvature signal into a solver-allocation weight `Lambda(t)`:
- step schedule: switch from Euler to Heun when `kappa_hat(i)` crosses threshold `tau_k`;
- linear/cosine schedules: blend `x = Lambda x_E + (1-Lambda) x_H`.
- Update the state with the selected or blended solver and continue.
- Separately, for adaptive scheduling, estimate a local variation proxy `S_hat(t)` for the vector field and choose step sizes that satisfy the Wasserstein-derived bound `Delta t <= sqrt(2 eta / S_hat)`.
- If a fixed number of steps is required, resample the resulting adaptive path to a fixed N-step schedule by uniformly discretizing a weighted geodesic-length proxy.
- Return the final sample.
state_variables_and_history=Current sample `x_i`; current and previous vector fields `v_i`, `v_{i-1}`; previous step size; curvature proxy `kappa_hat(i)`; optional adaptive timestep ledger and Wasserstein error budget `eta`.
nfe_accounting=The adaptive solver part is zero-extra-NFE because it uses cached vector fields already computed by the base solver. The adaptive scheduler itself is also training-free, but in practice it changes the time grid and may use extra offline search/precomputation.
portability=direct
repo_transfer_hypothesis=The portable part for this repo is the adaptive solver gate, not the schedule optimizer: use the cached drift change to selectively promote a late step from the current relaxed predictor-corrector form to an exact Heun step only when local curvature is high, while preserving the paper-qualified `{3,4}` UniPC tail and the fixed EDM schedule.
failure_or_reject_boundary=Reject direct use of the adaptive scheduler component because this repo already saw a decisive schedule-law paper miss and because SDM's timetable search changes the grid globally. The useful transfer is the cache-based curvature-triggered solver allocation.
citation_followups=EDM; DPM-Solver; COS; Jump Your Steps; probabilistic ODE solver stiffness analysis
status=ready

## Paper Entry

paper_id=dual_solver_2026
title=Dual-Solver: A Generalized ODE Solver for Diffusion Models with Dual Prediction
authors=Soochul Park; Yeon Ju Lee
venue_or_source=ICLR 2026
year=2026
url=https://arxiv.org/abs/2603.03973
pdf_path=literature/pdfs/dual_solver_2603.03973.pdf
family=learned dual-prediction solver with learned integration domain and residual coefficients
why_relevant=This is a recent independently discovered solver paper that initially looks close to the repo's low-NFE regime, but it is useful mainly as a reject boundary because its gains come from learning per-step coefficients and timesteps.
core_claim=A generalized predictor-corrector solver with learnable parameters controlling prediction type, integration domain, and second-order residual terms can outperform existing few-step solvers when the parameters are optimized end-to-end with a classifier-based objective.
assumptions=The solver parameters and timesteps can be learned offline by backpropagating through the full sampling process using a pretrained classifier or CLIP model; the backbone exposes both `x_theta` and `epsilon_theta` or allows conversion between them.
complete_sampling_pseudocode=
- Inputs: pretrained diffusion backbone, initial noise `x_T`, timesteps `{t_i}`, predictor-corrector solver family with learnable per-step parameters `gamma`, `tau`, `kappa`, and a pretrained classifier or CLIP model for optimization.
- At inference, run a first-order predictor to produce a provisional sample `x'_{t_{i+1}}` from the current state and current model outputs.
- Evaluate the model at the provisional sample and apply a second-order corrector whose coefficients are determined by the learned per-step parameter set.
- Repeat until the final time is reached.
- Offline, optimize all stepwise solver parameters and intermediate timesteps end-to-end so the final decoded image minimizes a classification or CLIP loss, updating the parameters with backpropagation through the sampler.
state_variables_and_history=Current state; predictor and corrector parameter sets for each step; optional converted dual predictions `x_theta` and `epsilon_theta`; learned timesteps; classifier loss targets.
nfe_accounting=Sampling-time NFE can match a standard predictor-corrector sampler, but the method depends on offline learned parameters and learned timesteps.
portability=incompatible
repo_transfer_hypothesis=The only portable lesson is that prediction type and integration domain matter and may vary by step. A faithful Dual-Solver port is out of scope because it requires learned coefficients, learned timesteps, and external optimization machinery.
failure_or_reject_boundary=Reject direct use because the method's value comes from offline parameter learning, which violates the fixed-pretrained, `sample.py`-only contract.
citation_followups=DPM-Solver++; BNS-Solver; DS-Solver; CLIP-based solver learning
status=ready

## Paper Entry

paper_id=dpm_solver_2022
title=DPM-Solver: A Fast ODE Solver for Diffusion Probabilistic Model Sampling in Around 10 Steps
authors=Cheng Lu; Yuhao Zhou; Fan Bao; Jianfei Chen; Chongxuan Li; Jun Zhu
venue_or_source=NeurIPS 2022
year=2022
url=https://arxiv.org/abs/2206.00927
pdf_path=literature/pdfs/dpm_solver_2206.00927.pdf
family=dedicated exponential-integrator diffusion ODE solver
why_relevant=This older seminal paper is the clean reference for the "higher-order only where it matters" part of the new SDM pass. It explains how the dedicated diffusion ODE structure changes what a high-order step should look like and helps distinguish principled solver promotion from arbitrary late-step patches.
core_claim=By analytically integrating the linear part of the diffusion ODE and approximating only the exponentially weighted neural-network integral, one can build dedicated first-, second-, and third-order solvers that work in the few-step regime far better than black-box ODE solvers.
assumptions=The diffusion ODE can be expressed with known `alpha_t`, `sigma_t`, and log-SNR `lambda`; the model predicts the noise term or an equivalent representation; one can evaluate the model at the current state and a small number of intermediate states.
complete_sampling_pseudocode=
- Inputs: initial noisy sample `x_T`, reverse timesteps `{t_i}`, corresponding `lambda_i = log(alpha_i / sigma_i)`, trained noise predictor `epsilon_theta`.
- For each step from `t_{i-1}` to `t_i`, write the exact solution as the analytically integrated linear term plus an exponentially weighted integral of `epsilon_theta`.
- First-order version:
- `x_i = alpha_i/alpha_{i-1} * x_{i-1} - sigma_i (exp(h_i)-1) * epsilon_theta(x_{i-1}, t_{i-1})`.
- Second-order version:
- Evaluate an intermediate state at the lambda midpoint `s_i`, run the model there, and use that midpoint prediction in the final update over the full interval.
- Third-order version:
- Evaluate two intermediate states, form finite-difference terms, and use them in the final exponential-integrator update.
- Continue until `t_M = 0`.
state_variables_and_history=Current state; optional midpoint or two-point intermediate states; log-SNR step size `h_i`; model evaluations at current and intermediate states.
nfe_accounting=Zero extra NFE relative to the chosen order: order-1 uses one evaluation, order-2 uses two, order-3 uses three. There is no offline training.
portability=direct
repo_transfer_hypothesis=The full global DPM-Solver family is too disruptive for the current paper winner, but the portable lesson is that exact or dedicated higher-order promotion should be reserved for the genuinely high-curvature late regime rather than sprayed uniformly over the entire trajectory.
failure_or_reject_boundary=Reject a full global swap because earlier localized DPM-Solver++/ERA-style probes already weakened or lost here. The useful role of DPM-Solver in this pass is as the solver-design baseline that SDM's curvature gate decides when to promote toward.
citation_followups=DPM-Solver++; UniPC; SDM adaptive solvers
status=ready

## Session Takeaway

- `SDM` contributes a direct, zero-extra-NFE cache-based curvature gate that is still open in this repo because it changes *when* a stronger step is used rather than changing the schedule or introducing a new endpoint formula.
- `Dual-Solver` is a clean reject boundary: learned per-step coefficients and learned timesteps are out of scope even though the inference-time predictor-corrector pattern looks familiar.
- `DPM-Solver` provides the older solver-design reference for why late curvature should trigger a more exact step, but not necessarily a global solver swap.
- The next clean synthesized target is therefore a conservative curvature-gated exactization step immediately before the existing `{3,4}` UniPC window, leaving the paper-qualified tail structure intact.

## Candidate Card

family=curvature_gated_late_exactization
kind=mechanism
external_anchor=Formalizing the Sampling Design Space of Diffusion-Based Generative Models via Adaptive Solvers and Wasserstein-Bounded Timesteps (Jo & Choi, 2026); DPM-Solver (Lu et al., 2022)
borrowed_mechanism=use a cached relative-curvature proxy to decide when a late step should be promoted from a cheaper approximate update to a more exact higher-order one
synthesis_step=keep the exact `5e43179` sampler everywhere, including the `{3,4}` localized UniPC window and the last two exact-Heun stages, but add an SDM-style sample-wise curvature gate on non-UniPC late standard steps that collapses the current relaxed predictor-corrector update to exact Heun only when the cached relative curvature exceeds a conservative threshold
portability=direct
base_commit=6b1e3f6
active_nf_range=paper-targeted full-step regime only; the branch is dormant when `num_steps < 12`, so NFE 5/9/11/13 should remain unchanged
extra_nfe=0
hypothesis=the current paper winner may only need extra exactness on the single high-curvature step immediately before the `{3,4}` UniPC window, and a curvature trigger can supply that selectively without reopening the failures from fixed schedule warps, forward-value placement, or block extrapolation
expected_signature=the proxy frontier at NFE 5/9/11/13 stays inside the current stable band while `fid_N35` improves below `6.7513`; if promoted, paper block 0 should beat `1.93345` or at least show a cleaner same-sign move than the recent misses
ablation=if this wins, compare against the same code path with the curvature threshold raised high enough to disable the gate, to isolate the gain from the adaptive trigger rather than from incidental refactoring
kill_condition=any `fid_N35` regression, any low-NFE drift outside the stable band, or any paper block-0 miss that looks like another clear translation failure

## Candidate Card

family=localized_dpm_solver2_preterminal_midpoint
kind=mechanism
external_anchor=DPM-Solver (Lu et al., 2022); Formalizing the Sampling Design Space of Diffusion-Based Generative Models via Adaptive Solvers and Wasserstein-Bounded Timesteps (Jo & Choi, 2026)
borrowed_mechanism=replace one late higher-order step with a dedicated lambda-midpoint DPM-Solver-2 update that analytically targets the diffusion ODE structure rather than using a generic endpoint corrector
synthesis_step=keep the exact `5e43179` base everywhere except the first pre-terminal `{steps_left=4}` UniPC step; on that single step, replace the local UniPC correction with a VE-form DPM-Solver-2 midpoint update in log-SNR/lambda midpoint sigma, while preserving the second `{steps_left=3}` UniPC step and the last two exact-Heun stages
portability=direct
base_commit=24aa494
active_nf_range=paper-targeted full-step regime only; the branch is dormant when `num_steps < 12`, so NFE 5/9/11/13 should remain unchanged
extra_nfe=0
hypothesis=the two-step `{3,4}` paper-qualified window may still need two distinct late mechanisms: a dedicated midpoint exponential-integrator step at `{4}` to enter the terminal zone cleanly, followed by the existing history-aware UniPC correction at `{3}`
expected_signature=the proxy frontier at NFE 5/9/11/13 stays inside the current stable band; if promoted, paper block 0 should improve over `1.93345` or at least beat the recent exactization miss and justify a full-row continuation
ablation=if this wins, compare against the same code path with the midpoint branch disabled so `{4}` falls back to the original UniPC step, isolating whether the gain comes from the midpoint solver itself rather than from refactoring
kill_condition=any low-NFE drift outside the stable band, any proxy instability, or any paper block-0 result that clearly trails the `5e43179` base

## Candidate Card

family=localized_dpm_solver2_preterminal_midpoint
kind=ablation
external_anchor=DPM-Solver (Lu et al., 2022)
borrowed_mechanism=keep the same dedicated lambda-midpoint solver substitution but move its placement within the two-step pre-terminal window
synthesis_step=from the new paper base `3d0ecd6`, relocate the localized DPM-Solver-2 midpoint branch from `{steps_left=4}` to `{steps_left=3}` so the earlier step falls back to the original UniPC correction while the later pre-terminal step takes the midpoint solver update
portability=direct
base_commit=1d36e19
active_nf_range=paper-targeted full-step regime only; the branch remains dormant when `num_steps < 12`
extra_nfe=0
hypothesis=if the win is truly tied to the *placement* of the midpoint solver on the first pre-terminal step, then moving it one step later should weaken the paper path even if the proxy band stays effectively unchanged
expected_signature=the proxy frontier remains inside the usual stable band; if promoted, paper block 0 should land above the new `3d0ecd6` base `1.92757`, confirming that the step-4 placement is the active ingredient
ablation=this is the first same-family placement ablation required after the paper promotion; if it weakens, the current `3d0ecd6` story becomes much sharper
kill_condition=any low-NFE drift outside the stable band, any proxy instability, or any paper block-0 result that is not clearly weaker than `3d0ecd6`

## Candidate Card

family=localized_dpm_solver2_preterminal_midpoint
kind=ablation
external_anchor=DPM-Solver (Lu et al., 2022)
borrowed_mechanism=keep the same dedicated lambda-midpoint solver substitution but widen it across the entire two-step pre-terminal window
synthesis_step=from the restored `3d0ecd6` paper base, activate the localized DPM-Solver-2 midpoint branch on both `{steps_left=4}` and `{steps_left=3}` so the full pre-terminal tail becomes a two-step midpoint-solver block and the history-aware UniPC correction is removed only inside that window
portability=direct
base_commit=c0f176b
active_nf_range=paper-targeted full-step regime only; the branch remains dormant when `num_steps < 12`
extra_nfe=0
hypothesis=if the `3d0ecd6` gain comes mostly from introducing midpoint diffusion-ODE structure anywhere in the pre-terminal tail, then widening the midpoint branch to both late steps could preserve or improve the paper path; if it weakens, the mixed midpoint-at-`{4}` plus UniPC-at-`{3}` composition is the real mechanism
expected_signature=the proxy frontier should remain inside the usual stable band; if promoted, paper block 0 will likely land above `1.92757` if the mixed tail is minimal, but a surprise improvement would argue that the second late step also prefers midpoint integration over history correction
ablation=this is the complementary same-family consolidation probe after the `{steps_left=3}` placement miss; together the two ablations test whether placement or two-step widening can explain the paper win
kill_condition=any low-NFE drift outside the stable band, any proxy instability, or any paper block-0 result that clearly trails the `3d0ecd6` base

## Paper Entry

paper_id=rex_2026
title=Rex: A Family of Reversible Exponential (Stochastic) Runge-Kutta Solvers
authors=Zander W. Blasingame; Chen Liu
venue_or_source=arXiv
year=2026
url=https://arxiv.org/abs/2502.08834
pdf_path=literature/pdfs/rex_2502.08834.pdf
family=reversible exponential Runge-Kutta solvers with Lawson-transformed diffusion dynamics
why_relevant=This is a recent independently discovered solver paper that at first looks like a route to a fresh diffusion-ODE update family, but it is most useful here for separating genuinely new reversible machinery from Princeps steps that reduce to already-known DPM/DDIM-style solvers.
core_claim=By applying a Lawson transform to the semilinear diffusion ODE/SDE, building an explicit RK-based transformed solver `Princeps`, and then coupling it with a McCallum-Foster-style reversible shadow-state update, one can obtain algebraically reversible diffusion solvers with the same convergence order as the underlying RK method.
assumptions=Known diffusion schedule functions `alpha_t`, `sigma_t`, or equivalent transformed coordinates; explicit RK or SRK coefficients; ability to maintain an auxiliary shadow state and, for the SDE case, replay the same Brownian path.
complete_sampling_pseudocode=
- Inputs: current diffusion state `x_n`, auxiliary shadow state `xhat_n`, transformed time coordinate `varsigma`, integrating-factor weight `kappa_n`, coupling parameter `zeta`, and an explicit RK/SRK base scheme `Phi`.
- Construct `Princeps`:
- Rewrite the diffusion ODE/SDE into a transformed state `Y` via integrating factor and time change so `dY/dvarsigma = f_theta(varsigma, Xi(varsigma) Y)` (plus Brownian noise in the SDE case).
- Apply the chosen explicit RK/SRK scheme `Phi` in the transformed coordinates to obtain an increment `Psi_h`.
- Map the update back to the original state variable with the schedule-dependent weights.
- Construct `Rex` forward step:
- `x_{n+1} = (kappa_{n+1}/kappa_n) * (zeta * x_n + (1-zeta) * xhat_n) + kappa_{n+1} * Psi_h(varsigma_n, xhat_n)`.
- `xhat_{n+1} = (kappa_{n+1}/kappa_n) * xhat_n - kappa_{n+1} * Psi_{-h}(varsigma_{n+1}, x_{n+1})`.
- Backward step mirrors the forward equations with the same `Psi_h/Psi_{-h}` pair, recovering the previous state exactly in algebraic form.
- For ODE sampling only, the portable core is just `Princeps`; the reversibility benefit comes only when the auxiliary shadow-state coupling is also kept.
state_variables_and_history=Current sample `x_n`; auxiliary shadow state `xhat_n`; transformed time variable; integrating-factor weights `kappa_n`; optional Brownian increments or PRNG seed for SDE reversibility; RK stage states for `Princeps`.
nfe_accounting=Princeps inherits the NFE of the chosen RK order, but Rex adds paired forward/backward Princeps evaluations and auxiliary-state bookkeeping to realize reversibility.
portability=partial
repo_transfer_hypothesis=The only direct-looking piece is `Princeps`, but the paper itself shows that Princeps subsumes DDIM, DPM-Solver-1/2/12, DPM-Solver++(2S), SEEDS-1, and gDDIM. The new value of Rex is reversibility, not a clearly better forward-only sampler update for this repo.
failure_or_reject_boundary=Reject Rex proper as a serious next family because its novelty depends on the reversible shadow-state machinery and backward Princeps step, which target inversion/editing rather than forward FID. Treat Princeps as a unifying lens that collapses back into already-tested DPM-style moves rather than a fresh family.
citation_followups=DPM-Solver; DPM-Solver++; DDIM; SEEDS; gDDIM; McCallum-Foster reversible methods
status=ready

## Paper Entry

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

## Paper Entry

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

## Paper Entry

paper_id=tap_2026
title=TAP: A Token-Adaptive Predictor Framework for Training-Free Diffusion Acceleration
authors=Haowei Zhu; Tingxuan Huang; Xing Wang; Tianyu Zhao; Jiexi Wang; Weifeng Chen; Xurui Peng; Fangmin Chen; Junhai Yong; Bin Wang
venue_or_source=arXiv
year=2026
url=https://arxiv.org/abs/2603.03792
pdf_path=literature/pdfs/tap_2603.03792.pdf
family=token-adaptive predictor selection for diffusion transformers
why_relevant=This recent independently discovered acceleration paper is important because it offers a modern predictor-selection viewpoint, but only through model-internal token routing that is incompatible with this repo. It therefore sharpens the boundary between valid sampler research and transformer compute scheduling.
core_claim=A single first-layer probe can estimate per-token predictor error well enough to let a diffusion transformer choose a different cached/predicted feature update for each token and step, improving the quality-efficiency frontier over global predictor policies.
assumptions=Diffusion transformer architecture with tokenized hidden states; access to first-layer modulated inputs and residual caches; ability to replace downstream token computations selectively; prediction windows over hidden-feature trajectories.
complete_sampling_pseudocode=
- Inputs: current transformer hidden state `x_t`, cached first-layer modulated inputs and residuals from earlier full steps, predictor family `P` with different Taylor orders and horizons, probe distance metric.
- Every `N`th step perform a full model evaluation, cache the first-layer modulated input and residual features.
- On accelerated steps, predict each token's future hidden feature under every candidate predictor in `P`.
- Use a first-layer probe to compute a per-token proxy loss for each candidate predictor.
- Select the lowest-proxy-loss predictor independently for each token.
- Use the selected tokenwise predicted residuals to replace the full model computation for that step.
- Repeat over the denoising trajectory.
state_variables_and_history=Tokenwise hidden features; cached first-layer modulated inputs; residual caches; predictor family over Taylor order and horizon; tokenwise proxy losses.
nfe_accounting=The method reduces wall-clock cost by replacing or skipping large fractions of model-internal computation rather than by preserving an unchanged sampler at fixed model cost.
portability=incompatible
repo_transfer_hypothesis=The direct transfer is negative: adaptive predictor selection can be powerful, but only when one has token-level access to model internals. The portable lesson is merely that disagreement-based selection can be used as a proxy signal, not that token-adaptive acceleration itself can be ported here.
failure_or_reject_boundary=Reject direct use because this repo exposes only sampler-level state in `sample.py`, not token-level transformer features or model-internal routing hooks.
citation_followups=TaylorSeer; TeaCache; SpeCa; ToCa; FoCa; FreqCa
status=ready

## Paper Entry

paper_id=pdns_2025
title=Proximal Diffusion Neural Sampler
authors=Wei Guo; Jaemoo Choi; Yuchen Zhu; Molei Tao; Yongxin Chen
venue_or_source=arXiv
year=2025
url=https://arxiv.org/abs/2510.03824
pdf_path=literature/pdfs/pdns_2510.03824.pdf
family=proximal point diffusion neural sampler trained over path measures
why_relevant=This recent independently discovered paper is not a direct inference-time sampler for a fixed pretrained model, but it provides a clear proximal-regularization viewpoint that can inspire a training-free trust-region-style correction family in `sample.py`.
core_claim=Instead of solving a single global stochastic optimal-control problem for a neural diffusion sampler, one can run proximal iterations in path-space, repeatedly solving local KL-regularized subproblems and training a new controlled diffusion process against proximal weighted denoising cross-entropy targets to improve mode coverage and stability.
assumptions=Neural sampler is trainable; one can optimize model parameters over repeated proximal iterations; stochastic optimal-control or denoising-cross-entropy training infrastructure is available; reference and target path measures are known.
complete_sampling_pseudocode=
- Inputs: reference path measure `P_ref`, current neural sampler path measure `P_{theta_{k-1}}`, target reward `r(X_T)`, proximal step size `eta_k`.
- For proximal iteration `k`, define the local subproblem:
- minimize `-E_P[r(X_T)] + KL(P || P_ref) + (1/eta_k) * KL(P || P_{theta_{k-1}})`.
- Sample trajectories from the previous neural sampler and compute proximal path weights relative to `P_ref` and the terminal reward.
- Train a new neural control or score network with a proximal weighted denoising cross-entropy or equivalent bridge-matching loss.
- Set the new sampler as `P_{theta_k}` and repeat.
- At the end of training, use the learned controlled diffusion to sample from the target distribution.
state_variables_and_history=Current neural sampler parameters; previous proximal iterate; proximal step size schedule; trajectory weights; terminal rewards; reference path measure.
nfe_accounting=Inference-time NFE can resemble that of a controlled diffusion sampler, but the method fundamentally depends on repeated training and proximal optimization over path measures.
portability=incompatible
repo_transfer_hypothesis=The direct method is out of scope, but the paper does suggest a portable synthesis idea: when a higher-order step looks too aggressive, regularize it toward a simpler local companion using an error- or disagreement-based trust weight rather than replacing the whole trajectory or retraining a sampler.
failure_or_reject_boundary=Reject faithful transfer because PDNS is a training procedure for learning a new neural sampler, not an inference-time update that can be implemented in `sample.py` on a fixed pretrained EDM backbone.
citation_followups=Path Integral Sampler; weighted denoising cross-entropy samplers; diffusion Schrodinger bridge methods
status=ready

## Session Takeaway

- `Rex` closes off another tempting transformed-RK branch: its genuinely new part is reversibility with a shadow state, while the forward-only portable core mostly collapses back into DDIM/DPM/SEEDS-style exponential-integrator solvers.
- `F-scheduler` is a clean reject boundary for schedule work that depends on decoder tolerance, latent truncation, or Free-U U-Net decoration rather than on a pure sampler-side mechanism.
- `FSampler` and `TAP` are both strong evidence that many recent diffusion speedups come from changing NFE accounting or model-internal adaptive compute, not from a same-budget sampler update; the only portable residue is disagreement-based confidence signaling.
- `PDNS` is incompatible as a direct method, but its proximal viewpoint suggests a new in-bounds synthesis: keep a higher-order step only when its embedded local error is small, and otherwise shrink it toward a simpler companion without changing NFE.
- The next clean synthesized target is therefore an embedded trust-region family on top of the current `3d0ecd6` base: use the free Euler-vs-midpoint disagreement inside the existing DPM entry step as a local trust signal, and proximal-shrink the midpoint update toward its first-order companion when the embedded error is large.

## Candidate Card

family=embedded_proximal_midpoint_trust_region
kind=mechanism
external_anchor=Proximal Diffusion Neural Sampler (Guo et al., 2025); Rex: A Family of Reversible Exponential (Stochastic) Runge-Kutta Solvers (Blasingame & Liu, 2026)
borrowed_mechanism=combine a proximal conservative-update idea with an embedded Euler-versus-midpoint pair that provides a free local error signal inside the same two-call DPM-style step
synthesis_step=keep the exact `3d0ecd6` paper base everywhere, but on the pre-terminal `{steps_left=4}` midpoint branch compute both the first-order Euler companion and the second-order midpoint update, then use their normalized disagreement to shrink the midpoint proposal back toward the Euler companion when the embedded local error is large, without changing NFE or the downstream `{steps_left=3}` UniPC correction
portability=direct
base_commit=1705480
active_nf_range=paper-targeted full-step regime only; the branch remains dormant when `num_steps < 12`
extra_nfe=0
hypothesis=the `3d0ecd6` win may contain a real midpoint-direction benefit but still overshoot on a subset of trajectories; an embedded trust-region shrink could preserve the good direction while damping the rare over-aggressive step, potentially improving paper block 0 without reopening the wide misses from placement or whole-window rewrites
expected_signature=the low-NFE proxy band should stay inside the usual dormant range; if promoted, paper block 0 should beat `1.92757` or at least sit materially closer to the base than the `{3}`-placement and `{3,4}`-widening ablation losses
ablation=if this wins, rerun with the trust shrink disabled to recover exact `3d0ecd6`, and with a fixed constant shrink weight, to verify that adaptive embedded-error control rather than simple under-relaxation is the active ingredient
kill_condition=any low-NFE drift outside the stable band, any proxy instability, or any paper block-0 result that clearly loses to `3d0ecd6`

## Candidate Card

family=embedded_proximal_midpoint_trust_region
kind=tuning
external_anchor=Proximal Diffusion Neural Sampler (Guo et al., 2025); Rex: A Family of Reversible Exponential (Stochastic) Runge-Kutta Solvers (Blasingame & Liu, 2026)
borrowed_mechanism=keep the same embedded Euler-versus-midpoint trust-region idea but weaken the maximum proximal shrink after the first full-row result showed a small, same-sign over-damping
synthesis_step=from the restored `3d0ecd6` base, reintroduce the embedded midpoint trust-region branch exactly as in `5ef8741` but reduce the maximum shrink cap from `0.35` to `0.20`, leaving the disagreement formula and every other sampler component untouched
portability=direct
base_commit=f45c798
active_nf_range=paper-targeted full-step regime only; the branch remains dormant when `num_steps < 12`
extra_nfe=0
hypothesis=if the first trust-region probe lost only because it damped the good midpoint correction too aggressively, then a smaller cap should preserve the near-tie behavior while giving back enough midpoint strength to beat the `3d0ecd6` mean
expected_signature=the low-NFE proxy band should remain in the usual dormant range; if promoted, the paper row should stay near the incumbent on blocks 0 and 1 while improving block 2 enough to recover the mean gap
ablation=this is the one allowed scalar follow-up after the initial full-row near-tie; if it also loses, stop tuning the trust cap and rotate away from the family
kill_condition=any low-NFE drift outside the stable band, any proxy instability, or any paper row that remains clearly worse than the `3d0ecd6` base

## Session Addendum

Session date: 2026-03-14
Working paper base after the trust-region reject: `3d0ecd6`
Reason for new pass: the embedded midpoint trust-region family produced two full-row paper losses, so `program.md` requires a fresh literature rotation before the next family change.

## Paper Entry

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

## Paper Entry

paper_id=dyweight_2026
title=DyWeight: Dynamic Gradient Weighting for Few-Step Diffusion Sampling
authors=Tong Zhao; Mingkun Lei; Liangyu Yuan; Yanming Yang; Chenxi Song; Yang Wang; Beier Zhu; Chi Zhang
venue_or_source=arXiv
year=2026
url=https://arxiv.org/abs/2603.11607
pdf_path=literature/pdfs/dyweight_2603.11607.pdf
family=learned dynamic gradient weighting with implicit time calibration
why_relevant=This newly added 2026 paper is valuable mainly as a reject boundary and calibration read. It cleanly separates two ingredients that matter in few-step diffusion solvers: history weighting and time/step-size calibration. That framing is useful even though the paper's direct method is outside this repo's contract.
core_claim=Classical handcrafted multistep coefficients are suboptimal in the few-step diffusion regime; learning time-varying unconstrained history weights together with explicit time shifting and time scaling yields a better solver trajectory and state-of-the-art few-step quality.
assumptions=A high-fidelity teacher trajectory is available; per-step solver weights and time-scaling factors can be learned offline by distillation; the model can be queried repeatedly during teacher and student optimization.
complete_sampling_pseudocode=
- Inputs: pretrained diffusion model `D_theta`; teacher solver `S`; teacher schedule `T_teacher`; student schedule `T_student`; multistep order `K`; learnable student parameters `Phi = {W, s}`.
- Training stage:
- Sample initial noise `x_T`.
- Generate a high-step teacher sample `x_0^teacher = S(D_theta, x_T, T_teacher)`.
- Run the DyWeight student sampler from the same `x_T` using `Phi` and `T_student`.
- Minimize a terminal supervision loss `dist(x_0^student, x_0^teacher)` and update `Phi`.
- Sampling stage:
- Initialize `x_N = x_T`, current time `t_N`, and a fixed-length buffer of recent gradients.
- For each reverse step `n = N ... 1`:
- Query the model at the scaled time `s_n * t_n`.
- Convert the model output into the current gradient and push it into the history buffer.
- Read the step-specific weight row `w_n` from `W`.
- Form the weighted gradient combination `d_n = sum_i w_{n,i} * buffer[i]`.
- Update the sample with `x_{n-1} = x_n + d_n * (t_{n-1} - t_n)`.
- Shift the internal notion of the next query time using the same unconstrained weights: `tilde_t_{n-1} = t_n + sum_i w_{n,i} * (t_{n-1} - t_n)`.
- Continue until the final sample is produced.
state_variables_and_history=Current sample; per-step learned weight matrix `W`; per-step time-scaling vector `s`; gradient history buffer; teacher trajectory during optimization.
nfe_accounting=Inference-time NFE matches the underlying multistep solver order, but the method fundamentally depends on offline distillation and learned per-step parameters.
portability=incompatible
repo_transfer_hypothesis=The only portable lesson is conceptual: few-step solvers need both history weighting and time calibration. Under the frozen contract, that suggests a deterministic local scale-calibration signal, not learned weights or teacher supervision.
failure_or_reject_boundary=Reject any direct use because the gains come from learned per-step parameters and teacher-student optimization, both of which violate the fixed-pretrained `sample.py`-only contract.
citation_followups=iPNDM; DPM-Solver++; UniPC; S4S; LD3; EPD
status=ready

## Paper Entry

paper_id=stork_2025
title=STORK: Faster Diffusion And Flow Matching Sampling By Resolving Both Stiffness And Structure-Dependence
authors=Zheng Tan; Weizhen Wang; Andrea L. Bertozzi; Ernest K. Ryu
venue_or_source=arXiv
year=2025
url=https://arxiv.org/abs/2505.24210
pdf_path=literature/pdfs/stork_2505.24210.pdf
family=virtual-NFE stabilized Taylor orthogonal Runge-Kutta solver
why_relevant=This newly added 2025 paper is the strongest fresh structure-independent solver candidate I found, and it clarifies why that whole direction is awkward under the current repo goals. It tackles stiffness through many virtual substeps rather than through the diffusion-specific exponential-integrator structure.
core_claim=One can import stabilized Runge-Kutta ideas into diffusion and flow-matching sampling by replacing the many expensive substep model evaluations with Taylor-approximated virtual NFEs, yielding a structure-independent stiff solver that improves few-step quality across several models.
assumptions=The sampler can maintain multiple previous velocity evaluations; it can approximate time derivatives of the velocity by finite differences; it can run a multi-substep stabilized Runge-Kutta recurrence inside each outer diffusion step; an Adams-Bashforth/Euler bootstrap is available for the first steps.
complete_sampling_pseudocode=
- Inputs: diffusion or flow-matching model velocity/noise predictor; outer reverse schedule `{t_i}`; chosen stabilized Runge-Kutta order `k in {1,2,4}`; number of internal substeps `s`; Taylor approximation order.
- Bootstrap phase:
- Use Euler for the first outer step.
- Use short Adams-Bashforth startup steps until enough previous velocities are buffered for the chosen Taylor order.
- For each remaining outer step from `t_i` to `t_{i-1}`:
- Treat the outer interval as one super-step and initialize the first internal state `Y_0 = x_{t_i}`.
- Evaluate the real model velocity/noise at the start of the super-step.
- Approximate the remaining internal substep velocities with Taylor expansions around the current outer-step velocity, using finite differences built from buffered previous real velocities; these are the virtual NFEs.
- Propagate the internal states through the stabilized orthogonal Runge-Kutta recurrence using the chosen SRK coefficients and the virtual NFEs.
- Set `x_{t_{i-1}} = Y_s` after the final internal substep.
- Update the velocity history buffer and continue until `x_0`.
state_variables_and_history=Current outer-step sample; internal SRK states `Y_j`; buffered previous real velocities; finite-difference approximations of velocity derivatives; substep count `s`; Taylor order.
nfe_accounting=The method reduces actual NFE by replacing most substep evaluations with Taylor-approximated virtual NFEs, but it still changes the internal step structure substantially and requires a multi-substep recurrence inside each outer diffusion step.
portability=partial
repo_transfer_hypothesis=A fully global STORK port is too broad and too complex for this repo's simplicity goal, but the paper sharpens one useful lesson: late-step stiffness can be attacked by localized virtual-substep stabilization rather than by a global schedule rewrite. If explored here, it should be an extremely localized one-step probe, not a whole-trajectory transplant.
failure_or_reject_boundary=Reject a full STORK port if it requires many virtual substeps across the whole trajectory, broad bootstrap logic, or a large new recurrence that obscures the current mechanism story. That would overshoot the repo's "simple poster mechanism" target.
citation_followups=SRK / RKC methods; DPM-Solver++; UniPC; DEIS
status=ready

## Session Takeaway

- `DyWeight` reinforces a hard reject boundary: few-step solver coefficients and time shifts really do want to be step-specific, but learning them offline is out of scope here.
- `STORK` shows a second hard boundary: structure-independent stiff solvers can help, but the practical route uses many virtual substeps and bootstrap logic, which is too global and too complex to be the next clean repo mechanism.
- `Score Normalization for a Faster Diffusion Exponential Integrator Sampler` exposes a more portable residue than the current compensation family: late-stage error can come from score-magnitude miscalibration itself, not only from the direction of the history term.
- The previous `DualFast` / `DC-Solver` branch already rejected additive current-score and buffer compensation on the approach steps, so the next family should not be another additive history blend.
- The next clean synthesized target is therefore a localized online score-normalization family on top of `3d0ecd6`: keep the winning `{4}` midpoint plus `{3}` UniPC tail fixed, and calibrate only the two earlier approach steps with an online drift-norm reference rather than a learned or offline schedule.

## Candidate Card

family=localized_online_score_normalized_approach
kind=mechanism
external_anchor=Score Normalization for a Faster Diffusion Exponential Integrator Sampler (Xia et al., 2023); DyWeight: Dynamic Gradient Weighting for Few-Step Diffusion Sampling (Zhao et al., 2026)
borrowed_mechanism=time-varying score/gradient scale calibration so the fast solver sees a better-conditioned late integrand without extra model evaluations
synthesis_step=from the exact `3d0ecd6` paper base, keep the `{steps_left=4}` DPM-Solver-2 midpoint step and the `{steps_left=3}` UniPC corrector untouched, but on the two earlier approach steps `{5,6}` rescale the current drift toward the recent accepted-drift magnitude using an online per-sample norm reference from `prev_d_prime`, capped by the existing late predictor-ramp magnitude instead of a learned/offline table
portability=direct
base_commit=3d0ecd6
active_nf_range=paper-targeted late full-step regime only; NFE 5/9/11/13 should stay inside the usual dormant band because the branch is inactive when `num_steps < 12`
extra_nfe=0
hypothesis=the remaining paper gap may be a late approach-step scale-calibration problem rather than another direction or schedule problem; online norm calibration should feed the winning midpoint-plus-UniPC tail with a better-conditioned state while leaving the low-NFE frontier unchanged
expected_signature=the proxy frontier should remain inside the usual stable band; if promoted, paper block 0 should improve beyond the `3d0ecd6` base `1.92757` or at least outperform the recent trust-region near-ties
ablation=if this family wins, keep the same `{5,6}` window but replace the online norm ratio with a constant `1.0` or a fixed scalar so we can distinguish true online calibration from the mere existence of another late branch
kill_condition=any low-NFE drift outside the stable band, any instability on the approach steps, or any paper block-0 loss that clearly trails the `3d0ecd6` base

## Candidate Card

family=localized_stork_virtual_predictor
kind=mechanism
external_anchor=STORK: Faster Diffusion And Flow Matching Sampling By Resolving Both Stiffness And Structure-Dependence (Tan et al., 2025)
borrowed_mechanism=replace one late predictor evaluation with a virtual internal stage synthesized from the current drift and a finite-difference time derivative estimated from the previous real drift
synthesis_step=from the exact `3d0ecd6` base, keep the `{steps_left=4}` midpoint entry step and `{steps_left=3}` UniPC corrector untouched, but on the single earlier approach step `{5}` replace the usual relaxed predictor extrapolation with a STORK-inspired virtual predictor `d_virtual` at the predictor time, using `prev_d_cur` and `prev_h` to approximate the local time derivative without adding model calls
portability=direct
base_commit=3d0ecd6
active_nf_range=paper-targeted late full-step regime only; NFE 5/9/11/13 should remain in the dormant band because the branch is inactive when `num_steps < 12`
extra_nfe=0
hypothesis=the current paper base may still lose accuracy on the single standard-regime step immediately before the winning midpoint entry; a virtual internal stage tied to the actual predictor time could improve stiffness handling there without modifying the midpoint-plus-UniPC tail itself
expected_signature=the proxy frontier should stay in the usual stable band; if promoted, paper block 0 should land below `1.92757` or at least beat the recent `abb8a61` paper-side loss convincingly
ablation=if this family wins, keep the same `{5}` window but fall back to the original predictor extrapolation rule to verify that the gain comes from the virtual-stage construction rather than from another late-branch placement
kill_condition=any low-NFE drift outside the stable band, any instability, or any paper block-0 loss that clearly trails the `3d0ecd6` base

## Candidate Card

family=localized_stork_virtual_predictor
kind=tuning
external_anchor=STORK: Faster Diffusion And Flow Matching Sampling By Resolving Both Stiffness And Structure-Dependence (Tan et al., 2025)
borrowed_mechanism=apply the same virtual-stage predictor on a slightly wider late approach window to test whether the structural stiffening benefit is truly single-step or shared across the two late approach steps
synthesis_step=from the new paper base `e2379ec`, widen `RESEARCH_STANDARD_LOCAL_VIRTUAL_PREDICTOR_STEPS_LEFT` from `(5,)` to `(5, 6)` while keeping the virtual-stage formula, the `{4}` midpoint entry step, and the `{3}` UniPC corrector unchanged
portability=direct
base_commit=e2379ec
active_nf_range=paper-targeted late full-step regime only; NFE 5/9/11/13 should remain in the dormant band because the branch is still inactive when `num_steps < 12`
extra_nfe=0
hypothesis=if the STORK-style virtual-stage effect is really correcting late-step stiffness rather than one lucky placement, widening it across both approach steps `{5,6}` could preserve or slightly improve the paper row; if it weakens, the current `{5}`-only placement is the minimal transferable mechanism
expected_signature=the proxy frontier should remain in the usual stable band; if promoted, the paper row should stay near or beat `e2379ec`, while a clear loss would identify `{5}` as the active placement
ablation=this is the natural placement follow-up after the paper win; if it weakens, treat the current `{5}`-only branch as the minimal defensible family and stop widening this mechanism
kill_condition=any low-NFE drift outside the stable band, any instability, or any paper block-0 result that clearly trails the `e2379ec` base

## Session Addendum

Session date: 2026-03-15
Working paper base after widened STORK miss: `e2379ec`
Reason for new pass: the same-family STORK widening ablation weakened already on the 5k proxy, so `program.md` now wants the next branch to pair incumbent consolidation with an orthogonal literature-grounded family rather than more window widening.

## Paper Entry

paper_id=bns_2024
title=Bespoke Non-Stationary Solvers for Fast Sampling of Diffusion and Flow Models
authors=Neta Shaul; Uriel Singer; Ricky T. Q. Chen; Matthew Le; Ali Thabet; Albert Pumarola; Yaron Lipman
venue_or_source=arXiv
year=2024
url=https://arxiv.org/abs/2403.01329
pdf_path=literature/pdfs/bns_2403.01329.pdf
family=solver distillation over a bespoke non-stationary linear multistep family
why_relevant=This newly added paper is a strong fresh reference for the general "step-specific coefficients matter" thesis, and it is useful here mainly as a clean reject boundary because it achieves that flexibility through offline optimization over a large non-stationary solver family.
core_claim=A model-specific non-stationary solver family that subsumes common RK and multistep samplers can be optimized with a tiny parameter set against high-accuracy target trajectories, substantially improving low-NFE sampling without retraining the backbone.
assumptions=One has access to high-accuracy target trajectories or outputs; the sampler coefficients and timesteps may be optimized offline for the specific pretrained model; the solver may use arbitrary linear combinations of past states and velocities.
complete_sampling_pseudocode=
- Inputs: pretrained diffusion or flow velocity field `u_t`; N-step non-stationary solver parameters `theta = {T_n, (a_i, b_i)}`; initial noise sample `x_0`.
- Offline optimization stage:
- Sample many initial noises `x_0`.
- For each noise sample, generate a high-accuracy target output `x(1)` using a strong adaptive solver or dense teacher trajectory.
- Run the candidate non-stationary solver:
- Initialize an empty velocity matrix `U_{-1}`.
- For each step `i = 0 .. n-1`:
- Evaluate the model velocity at the current state and current step time.
- Append the new velocity to the history matrix `U_i`.
- Update the state with the non-stationary affine rule `x_{i+1} = x_0 * a_i + U_i * b_i`.
- After the final step, compare the produced sample to the high-accuracy target and optimize `theta` over the dataset.
- Inference stage:
- Freeze the learned `theta`.
- Re-run the same history-accumulating update for a fresh `x_0` and return the final sample.
state_variables_and_history=Initial noise `x_0`; current sample; full matrix of past velocities `U_i`; optimized per-step affine coefficients `a_i, b_i`; optimized timestep grid `T_n`.
nfe_accounting=Sampling-time NFE matches the chosen solver length, but the method fundamentally depends on an offline optimization stage and stored model-specific coefficients.
portability=incompatible
repo_transfer_hypothesis=The portable lesson is only conceptual: late-step coefficients can want model-specific, non-stationary behavior. A faithful BNS transfer is out of scope because this repo forbids offline solver optimization and stored learned coefficients.
failure_or_reject_boundary=Reject any direct BNS-like branch that learns or searches per-step coefficients, uses teacher targets, or turns `sample.py` into a model-specific distilled solver table.
citation_followups=ST transformations; DPM-Solver; Progressive Distillation; solver distillation papers
status=ready

## Paper Entry

paper_id=diff_solver_search_2025
title=Differentiable Solver Search for Fast Diffusion Sampling
authors=Shuai Wang; Zexian Li; Qipeng Zhang; Tianhui Song; Xubin Li; Tiezheng Ge; Bo Zheng; Limin Wang
venue_or_source=ICML 2025 / PMLR
year=2025
url=https://arxiv.org/abs/2505.21114
pdf_path=literature/pdfs/diff_solver_search_2505.21114.pdf
family=differentiable search over timesteps and solver coefficients
why_relevant=This newly added 2025 paper is useful because it squarely targets the same few-step diffusion-ODE regime as this repo, but reaches its gains through data-driven search over coefficients and timesteps rather than through a hand-designed training-free update.
core_claim=Classical Adams-style interpolation structure is suboptimal for diffusion models; if one reduces the solver design space to step locations plus a compact set of coefficients, those quantities can be optimized differentiably to produce stronger few-step samplers for both DDPM and rectified-flow models.
assumptions=The solver coefficients and timesteps may be searched offline against model outputs; one can optimize a compact parameter space with gradient-based search; the resulting searched solver is model- and schedule-specific.
complete_sampling_pseudocode=
- Inputs: pretrained diffusion model; parameterized N-step solver with step locations and coefficient table; optimization dataset of prompts or latent noises.
- Define a compact search space containing:
- the timestep grid for the target NFE budget,
- and a small coefficient vector for each update rule in the multistep solver.
- For each optimization iteration:
- Sample a batch of latent noises or prompts.
- Run the current candidate solver on the pretrained model to produce final samples.
- Evaluate the resulting objective used by the paper's differentiable search procedure and backpropagate through the sampling path into the solver parameters.
- Update both timesteps and solver coefficients.
- After convergence, freeze the searched parameters.
- Inference stage:
- Run the frozen searched solver exactly as a normal few-step sampler using the optimized timestep grid and coefficient table.
state_variables_and_history=Current sample; cached multistep velocities; searched timestep vector; searched coefficient tables; optimization objective state during search.
nfe_accounting=Inference-time NFE is fixed after the search, but the method depends on offline differentiable optimization of solver parameters.
portability=incompatible
repo_transfer_hypothesis=The main portable takeaway is negative: there is real headroom in step-specific coefficients, but this repo should approximate that only through simple deterministic local signals, not through offline solver search.
failure_or_reject_boundary=Reject any branch that introduces searched coefficient tables, searched timestep laws, or optimization loops outside `sample.py`; those are outside the fixed-pretrained research contract.
citation_followups=DPM-Solver++; UniPC; BNS; schedule-search papers; Adams-like multistep methods
status=ready

## Paper Entry

paper_id=consistency_solver_2025
title=Image Diffusion Preview with Consistency Solver
authors=Fu-Yun Wang; Hao Zhou; Liangzhe Yuan; Sanghyun Woo; Boqing Gong; Bohyung Han; Ming-Hsuan Yang; Han Zhang; Yukun Zhu; Ting Liu; Long Zhao
venue_or_source=arXiv
year=2025
url=https://arxiv.org/abs/2512.13592
pdf_path=literature/pdfs/consistency_solver_2512.13592.pdf
family=RL-trained general-linear multistep preview solver
why_relevant=This newly added paper is another sharp boundary case for few-step solver research. It is especially relevant because it learns a generalized high-order solver for deterministic PF-ODE preview consistency, which superficially resembles the repo's paper-path goal but relies on optimization machinery that the repo forbids.
core_claim=A lightweight solver parameterization derived from general linear multistep methods can be optimized with reinforcement learning so that few-step preview samples stay visually and semantically consistent with a full-step target trajectory.
assumptions=One may compare few-step previews to full-step target samples; solver weights are trainable; reinforcement learning or related optimization machinery is available; preview-target similarity rewards can be computed from auxiliary perceptual features.
complete_sampling_pseudocode=
- Inputs: pretrained diffusion model; trainable solver policy `Psi_theta`; full-step reference solver `Psi`; prompt or conditioning `c`; initial noise `z`.
- For each training iteration:
- Sample a prompt and initial noise.
- Generate a target image `x_gt` by running the full-step deterministic solver on the fixed pretrained model.
- Run the few-step trainable solver policy on the same prompt and noise to get a preview image `x_p`.
- Compute a similarity reward between preview and target using perceptual or structural feature metrics.
- Update the solver policy parameters with PPO or another RL optimizer.
- Inference stage:
- Freeze the learned solver policy.
- Run the few-step trainable solver to generate previews or final few-step outputs.
state_variables_and_history=Current sample; trainable solver-weight network; few-step history states required by the generalized multistep formula; reward features; PPO optimization state.
nfe_accounting=Inference-time NFE can stay low, but the method depends on a full offline RL optimization stage and auxiliary reward computation.
portability=incompatible
repo_transfer_hypothesis=The only portable lesson is that consistency with a strong full-step target is a meaningful objective. The actual solver mechanism is out of scope because it requires learned weights, reward engineering, and RL optimization.
failure_or_reject_boundary=Reject any direct ConsistencySolver-like branch that learns solver coefficients against preview-target rewards or needs auxiliary perceptual features, because that would violate the frozen-model, `sample.py`-only protocol.
citation_followups=general linear multistep methods; DPM-Solver; distillation and consistency-model papers; RL-for-solver optimization
status=ready

## Session Takeaway

- The three fresh papers reinforce the same hard boundary from different angles: BNS, differentiable solver search, and ConsistencySolver all improve few-step sampling by learning or searching step-specific solver parameters, which is real evidence that coefficient placement matters, but it is out of scope for this repo.
- Re-reading `PFDiff` and `FSampler` after the STORK widening miss sharpens a different portable residue: cached past information can still help even without learned coefficients if it is used to reposition a single late predictor state, not to skip calls, learn schedules, or globally rewrite the solver.
- `PFDiff` is especially instructive for higher-order solvers because, once the solver order is above 1, the paper drops the future-score anticipation and keeps only the past-score springboard. That is exactly the part that can be localized into this repo.
- With `e2379ec` now established as both the paper winner and the minimal STORK placement, the next orthogonal probe should keep the `{4}` midpoint plus `{3}` UniPC tail unchanged and replace the `{5}` virtual-drift construction with a past-score springboard at the predictor state.

## Candidate Card

family=localized_pfdiff_springboard_predictor
kind=mechanism
external_anchor=PFDiff: Training-Free Acceleration of Diffusion Models Combining Past and Future Scores (Wang et al., 2025); FSampler: Training-Free Acceleration of Diffusion Sampling via Epsilon Extrapolation (Vladimir, 2025)
borrowed_mechanism=use cached past denoising information to create a guarded one-step springboard state before the next real predictor evaluation, while keeping the full NFE budget and the downstream solver structure unchanged
synthesis_step=from the exact `e2379ec` paper base, disable the STORK virtual-drift branch on the single `{steps_left=5}` approach step and instead set the predictor-state evaluation point to a PFDiff-style springboard `x_spring = x_hat + alpha * h * prev_d_prime`, reusing the previous accepted slope as the past-score guide; keep the `{4}` midpoint entry step, `{3}` UniPC corrector, and terminal exact-Heun pair unchanged
portability=direct
base_commit=e2379ec
active_nf_range=paper-targeted late full-step regime only; NFE 5/9/11/13 should remain inside the stable dormant band because the branch is inactive when `num_steps < 12`
extra_nfe=0
hypothesis=the remaining full-step error may be predictor-state placement rather than predictor-slope extrapolation; a single past-score springboard could feed the winning midpoint-plus-UniPC tail with a better entering state without widening the STORK residue or touching the low-NFE frontier
expected_signature=the proxy frontier should remain in the usual stable band; if promoted, paper block 0 should stay near or improve on the `e2379ec` base `1.92366`, while a clear loss would reject the springboard-state family as less portable than the virtual-drift family
ablation=if this family shows life, compare the same `{5}` placement using `prev_d_cur` instead of `prev_d_prime` so we can separate accepted-slope springboarding from raw-drift reuse
kill_condition=any low-NFE drift outside the stable band, any instability, or any paper block-0 loss that clearly trails the `e2379ec` base

## Session Addendum

Session date: 2026-03-15
Working paper base after residualized-family closeout: `e2379ec`
Reason for new pass: the localized residualized virtual-predictor family spent its justified follow-up and closed with a clear proxy loss on `ca28f14`, so `program.md` requires another fresh external literature rotation before the next family.
Fresh externally discovered anchors for this pass: `TAP` (`arXiv:2603.03792`), `ETC` (`arXiv:2510.24129`), and `SADA` (`arXiv:2507.17135`).

## Paper Entry

paper_id=tap_2026
title=TAP: A Token-Adaptive Predictor Framework for Training-Free Diffusion Acceleration
authors=Haowei Zhu; Tingxuan Huang; Xing Wang; Tianyu Zhao; Jiexi Wang; Weifeng Chen; Xurui Peng; Fangmin Chen; Junhai Yong; Bin Wang
venue_or_source=arXiv
year=2026
url=https://arxiv.org/abs/2603.03792
pdf_path=literature/pdfs/tap_2603.03792.pdf
family=token-adaptive predictor selection for cached internal features
why_relevant=This is a fresh architectural boundary paper for adaptive predictor selection. It is useful because it isolates a real mechanism idea, namely choosing among a small family of temporal predictors using a low-cost proxy, while also making clear why a faithful reproduction is out of scope for this repo.
core_claim=Different tokens and timesteps prefer different predictors, so a single global Taylor-style predictor is suboptimal; using a first-layer probe to score multiple candidate predictors and assign the best one per token preserves quality while accelerating cached diffusion inference.
assumptions=The denoiser exposes internal token features and the first-layer modulated input; cached first-layer activations and output residuals are available; one may skip full downstream computation for selected tokens and replace it with feature predictions.
complete_sampling_pseudocode=
- Inputs: denoiser `f_theta`; predictor family `P`; cache window `N`; distance metric `d`.
- At the beginning of each `N`-step window:
- Run one full denoising pass for the current timestep.
- Cache the first-layer modulated input `h_t = Modulate(Norm1(x_t), s_t, g_t)` and the global residual `r_t = f_theta(x_t, t) - x_t`.
- On each skipped step inside the window:
- For every candidate predictor `p in P`, predict the cached modulated input `h_hat_{t,p}` from prior cached features using a Taylor-style or related local predictor.
- Compute a per-token proxy loss `L_p^{b,n} = d(h_hat_{t,p}^{b,n}, h_t^{b,n})`.
- Select the predictor with minimum proxy loss for each token: `p*(b,n) = argmin_p L_p^{b,n}`.
- Apply the corresponding predictor to the cached residuals, assemble the per-token predicted residual map `r_hat_t`, and form the predicted model output `f_hat_theta(x_t, t) = x_t + r_hat_t`.
- Continue denoising using the predicted output until the next full cache-refresh step.
state_variables_and_history=Current latent; cached first-layer modulated inputs; cached residuals; family of candidate Taylor predictors with varying order and horizon; per-token selected predictor ids.
nfe_accounting=The paper leaves the diffusion-step count unchanged but replaces substantial internal-network work with cached feature prediction, which is outside the repo's fixed external-sampler interface.
portability=incompatible
repo_transfer_hypothesis=The full token-adaptive mechanism is not portable to `sample.py`, but the paper is still useful as a boundary: adaptive predictor selection is real, yet here we can only transfer tiny state-level residues, not internal token-level probes or feature caches.
failure_or_reject_boundary=Reject any TAP-like branch that depends on internal transformer activations, token-wise predictor assignment, or layer-level feature caches. Those mechanisms require architecture hooks the repo does not permit.
citation_followups=TaylorSeer; TeaCache; FORA; FreqCa; ToCa
status=ready

## Paper Entry

paper_id=etc_2025
title=ETC: Training-Free Diffusion Models Acceleration with Error-Aware Trend Consistency
authors=Jiajian Xie; Hubery Yin; Chen Li; Zhou Zhao; Shengyu Zhang
venue_or_source=arXiv
year=2025
url=https://arxiv.org/abs/2510.24129
pdf_path=literature/pdfs/etc_2510.24129.pdf
family=step-wise denoising trend smoothing with progressive distribution
why_relevant=This is the main direct anchor for the new pass because it operates entirely at the level of model outputs across timesteps, not internal features, and its core idea is a simple recursive historical trend estimate that can plausibly be transferred into the late-step predictor logic in `sample.py`.
core_claim=Short-term residual reuse causes trajectory drift because error-corrected model outputs fluctuate; a recursively smoothed historical trend better captures the long-term denoising direction, and progressively distributing that trend across skipped steps preserves consistency while still accelerating inference.
assumptions=Model outputs evolve smoothly in time; one may compare model outputs across consecutive timesteps; a small number of initial full denoising steps are available before trend-based approximations begin; a model-specific tolerance threshold can decide how far to extend the approximation window.
complete_sampling_pseudocode=
- Inputs: diffusion model `epsilon_theta`; scheduler `phi`; decoder `D`; total sample steps `T`; conditioning `c`; pre-inference count `n`; smoothing factor `alpha`; error threshold `sigma`.
- Initialize latent `x`, estimated future trend `Delta = None`, approximation step count `k = 0`, and previous model output `P = None`.
- Warmup stage:
- For `t = T` down to `T - n`:
- Run the true model output `epsilon_theta(x, t, c)`.
- If this is the second evaluated step, initialize the trend with the first output difference.
- Otherwise update the trend recursively: `Delta <- (1 - alpha) * Delta + alpha * (epsilon_theta(x, t, c) - P)`.
- Set `P` to the current model output and update the latent with the scheduler.
- Approximation stage:
- While `t > 1`:
- For `j = 1 .. k`, reuse the last true output and distribute the estimated trend progressively:
- `epsilon'_theta(x, t-j, c) <- P + Delta / k` or more generally the `s / k` scaled trend for the `s`-th skipped step.
- Update the latent with the scheduler using the approximated output and move forward through the skipped window.
- After the skipped window, run one fresh true model evaluation at the next step.
- Compare the fresh output difference against the predicted trend; if the deviation is below threshold `sigma`, expand the future approximation window (`k <- k + 1`), otherwise contract it (`k <- k - 1`, bounded below by zero).
- Refresh the trend using the new true output: `Delta <- (1 - alpha) * Delta + alpha * (epsilon_theta(x, t, c) - P)`.
- Continue until the final denoising step, then decode.
- Offline threshold search:
- Perturb final latents using model-output differences from each timestep, measure perceptual similarity to original outputs, and identify the transition point from volatile planning to stable refinement as the model-specific tolerance threshold.
state_variables_and_history=Current latent; previous true model output `P`; recursive trend estimate `Delta`; warmup step count `n`; approximation window size `k`; optional threshold estimated offline from similarity curves.
nfe_accounting=The paper reduces effective model evaluations by skipping steps, but its central trend estimator itself adds no NFE and only requires storing prior model outputs and the recursive trend state.
portability=direct
repo_transfer_hypothesis=The full step-skipping and threshold search machinery is broader than the repo’s fixed-NFE goal, but the trend estimator is directly portable: replace a one-step drift difference on the sensitive late predictor step with a recursively smoothed historical drift trend, keeping the overall NFE and solver structure unchanged.
failure_or_reject_boundary=Reject any ETC-like branch that changes the official NFE budget, introduces offline threshold search, or relies on multi-step output reuse across whole denoising windows. The in-bounds residue is only the recursive trend estimate itself.
citation_followups=AdaptiveDiffusion; TeaCache; SADA; MagCache; ruptures trend-inflection analysis
status=ready

## Paper Entry

paper_id=sada_2025
title=Stability-guided Adaptive Diffusion Acceleration
authors=Ting Jiang; Yixiao Wang; Hancheng Ye; Zishan Shao; Jingwei Sun; Jingyang Zhang; Zekai Chen; Jianyi Zhang; Yiran Chen; Hai Li
venue_or_source=ICML 2025 / PMLR / arXiv
year=2025
url=https://arxiv.org/abs/2507.17135
pdf_path=literature/pdfs/sada_2507.17135.pdf
family=stability-guided step-wise and token-wise cache-assisted pruning with solver-aware approximations
why_relevant=This paper is a useful direct follow-up because it explicitly incorporates solver-side gradients into the approximation rule and gives a higher-order backward-step formula that is cleaner than naive residual reuse, even though its full token-wise pruning framework remains out of scope.
core_claim=Acceleration should be treated as a stability-prediction problem: use solver-aware local curvature information to decide when approximations are safe, and when skipping a step, approximate the next state or clean sample with higher-order Adams-Moulton or interpolation formulas aligned with the underlying ODE solver.
assumptions=The denoiser exposes either noise or flow velocity predictions; one may compute local trajectory gradients `y_t = dx_t / dt`; token-wise and step-wise sparsity can be changed on the fly; advanced samplers such as DPM-Solver++ or EDM consume clean-sample estimates.
complete_sampling_pseudocode=
- Inputs: diffusion or flow-matching model; chosen ODE solver; cached past trajectory states and gradients.
- At each timestep `t`, compute the current model output and the associated trajectory gradient `y_t = dx_t / dt`.
- Form a stability criterion from the extrapolation error and the local curvature of the velocity:
- Build a third-order backward extrapolated state estimate `x_hat_{t-1}` from future-known reverse-time states.
- Compute the second-order finite difference of the velocity `Delta^(2) y_t`.
- If `(x_{t-1} - x_hat_{t-1}) dot Delta^(2) y_t < 0`, the trajectory is considered locally stable and eligible for step-wise acceleration.
- Step-wise approximation path:
- Reuse the current model output and approximate the next state with a solver-aware Adams-Moulton formula, for example
- `x_hat_{t-1} = x_t - 5/6 * Delta t * y_t - 5/6 * Delta t * y_{t+1} + 2/3 * Delta t * y_{t+2}`.
- Convert the approximated state into a clean-sample estimate `x_0^t` compatible with the active solver.
- In later stable regions, use multistep interpolation on stored `x_0` values to approximate skipped steps.
- Token-wise path when unstable:
- Prune only stable tokens, recompute unstable ones, and reconstruct the full feature map from a cache.
- Continue sampling under the chosen solver.
state_variables_and_history=Current latent; current and recent solver gradients `y_t`; local curvature estimate `Delta^(2) y_t`; cached clean-sample estimates for interpolation; optional token caches.
nfe_accounting=The step-wise approximation path itself can preserve the external NFE budget if used as a local formula, but the full paper mainly targets architectural acceleration through skipping or pruning and therefore changes computation in ways broader than the repo allows.
portability=partial
repo_transfer_hypothesis=The token-wise pruning is incompatible, but the solver-aware lesson is useful: if we want to improve a late predictor in this repo, higher-order trend or curvature information should enter as a state-level drift estimate, not as another arbitrary scalar blend.
failure_or_reject_boundary=Reject any SADA-like branch that relies on token masks, internal caches, or dynamic skipping of official model evaluations. The portable residue is only a tiny solver-aware historical trend or multistep state estimate inside the fixed-NFE sampler.
citation_followups=AdaptiveDiffusion; DeepCache; TeaCache; PF-Diff; Adams-Moulton methods
status=ready

## Session Takeaway

- `TAP` is a clean architectural reject boundary: token-adaptive predictor selection is real, but it depends on internal layer hooks and cannot be faithfully compressed into a `sample.py`-only sampler.
- `ETC` gives the strongest direct residue for this repo: the right correction signal may be a recursively smoothed historical denoising trend, not the raw one-step residual that recent local families keep reusing.
- `SADA` corroborates the same direction from the solver side: when approximations help, they help by respecting the ODE trajectory and using structured historical gradient information rather than ad hoc reuse.
- The next direct family should therefore keep the exact `e2379ec` paper base and replace the single-step STORK history vector on the `{steps_left=5}` predictor step with a recursively smoothed trend built from recent drift differences.

## Candidate Card

family=localized_trend_consistent_virtual_predictor
kind=mechanism
external_anchor=ETC: Training-Free Diffusion Models Acceleration with Error-Aware Trend Consistency (Xie et al., 2025); SADA: Stability-guided Adaptive Diffusion Acceleration (Jiang et al., 2025)
borrowed_mechanism=replace the raw one-step late predictor trend with a recursively smoothed historical trend, preserving long-horizon direction while damping error-corrected fluctuations
synthesis_step=from the exact `e2379ec` paper base, keep the single `{steps_left=5}` virtual-predictor placement but introduce a recursive trend state `trend_cur = (1 - alpha) * trend_prev + alpha * (d_cur - prev_d_cur)` (initialized from the first available drift difference) and use that trend instead of `(d_cur - prev_d_cur)` inside the localized virtual predictor; keep the `{4}` midpoint entry step, `{3}` UniPC corrector, and terminal exact-Heun pair unchanged everywhere else
portability=direct
base_commit=e2379ec
active_nf_range=paper-targeted late full-step regime only; NFE 5/9/11/13 should remain in the usual dormant band because the modified branch is still inactive when `num_steps < 12`
extra_nfe=0
hypothesis=the current paper winner may still be slightly too sensitive to the most recent drift fluctuation on the approach step; using a recursively smoothed trend should preserve the useful late-direction information while damping the low-NFE softness that keeps appearing when raw history is perturbed
expected_signature=the proxy frontier should at least match the dormant-band stability of `e2379ec` while improving the late full-step signal; compared with the closed residualized family, the `NFE=5` point should stay tighter to base instead of softening
ablation=if this shows life, compare the same smoothed-trend construction using `(d_cur - prev_d_prime)` as the incoming trend increment, so we can separate smoothing from raw-drift history choice
kill_condition=any clear proxy loss versus `e2379ec`, any low-NFE drift outside the usual dormant band, or any sign that the smoothed trend simply behaves like another closed STORK-history tweak rather than a new family

## Candidate Card

family=localized_trend_consistent_virtual_predictor
kind=ablation
external_anchor=ETC: Training-Free Diffusion Models Acceleration with Error-Aware Trend Consistency (Xie et al., 2025); SADA: Stability-guided Adaptive Diffusion Acceleration (Jiang et al., 2025)
borrowed_mechanism=keep the recursive trend smoother but swap the previous-history anchor from the raw prior drift to the accepted prior corrected slope
synthesis_step=from commit `de25906`, keep the localized `{steps_left=5}` trend-consistent virtual predictor exactly as-is but change the incoming trend increment from `(d_cur - prev_d_cur)` to `(d_cur - prev_d_prime)` whenever the accepted previous slope is available, leaving the recursive smoothing coefficient, `{4}` midpoint entry step, `{3}` UniPC corrector, and terminal exact-Heun pair unchanged
portability=direct
base_commit=de25906
active_nf_range=paper-targeted late full-step regime only; NFE 5/9/11/13 should remain in the usual dormant band because only the single late predictor trend source changes
extra_nfe=0
hypothesis=the positive proxy sign suggests the smoothed trend itself is useful, but the current raw-drift increment may still be slightly stale for the lowest NFE point; anchoring the trend increment to the accepted previous slope could preserve the mid-band gains while tightening `NFE=5`
expected_signature=the frontier should improve on `de25906 = 2.607512` or at least keep the win while reducing the `NFE=5` softness; a reversal at `NFE=9`/`NFE=13` would mean the family is another fragile history tweak
ablation=if this loses clearly, close the trend-consistent family rather than stacking smoothing-factor scans
kill_condition=any clear proxy loss versus both `de25906` and `e2379ec`, any new instability, or any broader low-NFE drift outside the usual dormant band

## Session Addendum

Session date: 2026-03-15
Working paper base after adaptive-allocation closeout: `e2379ec`
Reason for new pass: the orthogonal adaptive-allocation family lost cleanly on proxy, so `program.md` requires a fresh 3-paper external literature rotation before another family change.
Fresh externally discovered anchors for this pass: `S4S` (`arXiv:2502.17423`), `TADA` (`arXiv:2506.21757`), and `A-FloPS` (`arXiv:2509.00036`).

## Paper Entry

paper_id=s4s_2025
title=S4S: Solving for a Diffusion Model Solver
authors=Eric Frankel; Sitan Chen; Jerry Li; Pang Wei Koh; Lillian J. Ratliff; Sewoong Oh
venue_or_source=arXiv
year=2025
url=https://arxiv.org/abs/2502.17423
pdf_path=literature/pdfs/s4s_2502.17423.pdf
family=learned solver-coefficient optimization and joint schedule optimization
why_relevant=This paper is a strong fresh boundary for the current repo because it argues that few-step diffusion sampling should optimize the overall solver directly rather than cling to textbook local-error coefficients, but it does so through an offline learned coefficient search that the repo cannot faithfully adopt.
core_claim=In the very low-NFE regime, standard ODE-solver invariants stop being the right target; directly learning time-dependent solver coefficients against a strong teacher solver gives a much better student sampler, and alternating coefficient-plus-schedule optimization works even better.
assumptions=A teacher solver with many NFEs is available; offline optimization over solver coefficients and optionally time steps is allowed; a relaxed training objective can perturb initial latents within a bounded ball during optimization.
complete_sampling_pseudocode=
- Inputs: pretrained diffusion model; teacher solver `Psi*`; student solver family `Psi_phi` with learnable time-dependent coefficients; fixed or learnable discretization schedule `{t_i}`; distance metric `d`; relaxation radius `r`.
- Build an offline dataset of teacher trajectories by drawing `x_T ~ N(0, sigma_T^2 I)` and storing `Psi*(x_T)` as the target end sample.
- Choose a solver family:
- LMS form: express each step update `x_i = linear_transport(x_{i-1}) - nonlinear_increment(Delta_i(phi))`, where `Delta_i(phi)` is a learned combination of recent model evaluations.
- Single-step form: express each step using learned intermediate evaluations and learned synthesis coefficients.
- Predictor-corrector form: learn coefficients for both predictor and correction synthesis.
- S4S coefficient optimization loop:
- Sample `(x'_T, x_T, Psi*(x_T))` from the offline set, initialized with `x'_T = x_T`.
- Run the student solver `Psi_phi(x'_T)` on the chosen low-NFE schedule.
- Minimize `d(Psi_phi(x'_T), Psi*(x_T))` while constraining `x'_T` to stay inside an `L2` ball of radius `r * sigma_T` around `x_T`.
- Update both the solver coefficients `phi` and the relaxed latent `x'_T`; project `x'_T` back into the ball if needed.
- Repeat until coefficient convergence.
- Optional S4S-Alt loop:
- Alternate between coefficient updates with schedule fixed and schedule updates with coefficients fixed, always using the same relaxed objective against the teacher end sample.
- Inference after training:
- Freeze the learned coefficients (and optional learned schedule) and run the resulting low-NFE solver normally from a fresh Gaussian latent to the final sample.
state_variables_and_history=Current sample; previous solver evaluations for LMS or PC variants; per-step learned coefficient tables; offline teacher outputs; relaxed latents used during coefficient search.
nfe_accounting=Inference NFE can match the chosen student solver, but obtaining the coefficients requires an offline optimization loop plus repeated teacher-solver calls that are outside the repo's inference-only protocol.
portability=partial
repo_transfer_hypothesis=The faithful S4S pipeline is out of scope, but it sharpens a useful lesson: if few-step quality depends on solver-specific residual structure rather than textbook coefficients, the repo should look for tiny direct, inference-time structural decompositions of the existing winner instead of more scalar retuning.
failure_or_reject_boundary=Reject any branch that introduces an offline optimization stage, learned coefficient tables, a stored teacher latent set, or schedule training. Only a hand-crafted direct residue inspired by the solver-design lesson is in bounds.
citation_followups=LD3; BNS; DPM-Solver++; UniPC; GITS; DMN
status=ready

## Paper Entry

paper_id=tada_2025
title=TADA: Improved Diffusion Sampling with Training-free Augmented DynAmics
authors=Tianrong Chen; Huangjie Zheng; David Berthelot; Jiatao Gu; Josh Susskind; Shuangfei Zhai
venue_or_source=NeurIPS 2025 / arXiv
year=2025
url=https://arxiv.org/abs/2506.21757
pdf_path=literature/pdfs/tada_2506.21757.pdf
family=training-free momentum / augmented-state diffusion dynamics
why_relevant=This is a fresh direct look at augmented dynamics: it keeps a pretrained diffusion model fixed, but changes the state evolution by lifting the ODE into a small momentum system and letting only a weighted linear combination of the augmented variables touch the network.
core_claim=A pretrained conventional diffusion model can be reused inside a momentum-style augmented ODE because the training objective is equivalent after a linear reweighting of the augmented state; the augmented dynamics inject useful pseudo-noise and can improve few-step quality without retraining.
assumptions=Sampling may evolve an augmented state `x_t in (R^d)^N`; one may analytically compute the augmented mean and covariance to obtain a time-dependent reweighting `r_t`; the final sample is recovered from the weighted combination passed through the pretrained `x_theta` predictor.
complete_sampling_pseudocode=
- Inputs: pretrained diffusion model `x_theta`; discretized times `{t_i}`; augmented-state dimension `N`; analytic augmented linear dynamics matrices `A_t`, `b_t`; transition kernel `Phi(t, s)`; optional multistep solver cache `Q`.
- Initialize the augmented latent `x_{t_0} ~ N(0, Sigma_{t_0})` in `N` coupled variables.
- For each step `i = 0 .. T-1`:
- Compute the augmented mean `mu_{t_i}` and covariance `Sigma_{t_i}` and form the reweighting `r_{t_i} = Sigma_{t_i}^{-1} mu_{t_i} / (mu_{t_i}^T Sigma_{t_i}^{-1} mu_{t_i})`.
- Form the network input as the weighted combination `(r_{t_i}^T ⊗ I_d) x_{t_i}` and query the pretrained model to obtain `x_hat = x_theta((r_{t_i}^T ⊗ I_d) x_{t_i}, t_i)`.
- Convert the prediction into the augmented force term
- `F_theta(x_t, t) = N! * x_hat - sum_{n=0}^{N-1} x_t^{(n)} / (n! * (1 - t)^n)` all divided by `(1 - t)^N`.
- Approximate the nonlinear integral `Psi_{t_i} ≈ ∫ Phi(t_{i+1}, tau) b_tau F_theta(x_tau, tau) d tau` with an existing ODE solver; if the solver is multistep, update the cache `Q` with the latest model prediction.
- Advance the augmented state by `x_{t_{i+1}} = Phi(t_{i+1}, t_i) x_{t_i} + Psi_{t_i}`.
- After the last step, return `x_theta((r_{t_T}^T ⊗ I_d) x_{t_T}, t_T)` as the sample prediction.
- Analyze the induced scalar network-input dynamics `y_t = (r_t^T ⊗ I_d) x_t`, which obey a standard drift term plus an extra pseudo-noise term coming from interactions among the augmented variables.
state_variables_and_history=Augmented state variables `x_t^(0..N-1)`; analytic mean `mu_t`; covariance `Sigma_t`; reweighting vector `r_t`; optional multistep solver cache; final weighted network input `y_t`.
nfe_accounting=The paper keeps the same model-call budget as the wrapped solver, but it adds extra augmented state variables, analytic transition machinery, and usually an additional stochasticity/detail hyperparameter through the augmented prior covariance.
portability=partial
repo_transfer_hypothesis=The full augmented-state system is broader than a clean `sample.py` one-off, but the portable residue is useful: separate a state-aligned linear drift from the late-step innovation before extrapolating, instead of treating the whole drift vector as equally worth carrying forward.
failure_or_reject_boundary=Reject any branch that requires changing the model interface, carrying a full augmented covariance schedule, or adding a second latent stream throughout the whole trajectory. The only attractive transfer is a tiny local momentum-style decomposition inside the existing late-step mechanism.
citation_followups=AGM; critically damped Langevin diffusion; exponential integrators; UniPC; DPM-Solver++
status=ready

## Paper Entry

paper_id=aflops_2026
title=A-FloPS: Accelerating Diffusion Models via Adaptive Flow Path Sampler
authors=Cheng Jin; Zhenyu Xiao; Yuantao Gu
venue_or_source=AAAI 2026 / arXiv
year=2026
url=https://arxiv.org/abs/2509.00036
pdf_path=literature/pdfs/aflops_2509.00036.pdf
family=flow-path reparameterization with adaptive linear-plus-residual velocity decomposition
why_relevant=This is the cleanest fresh direct source for a small inference-time decomposition mechanism. Its core adaptive step is local, model-agnostic, training-free, and explicitly designed to improve low-NFE high-order integration by peeling away a state-aligned linear drift before extrapolating the residual.
core_claim=Diffusion trajectories can be reparameterized into flow-matching form, and high-order few-step integration improves further when the velocity is decomposed each step into an adaptive linear drift `lambda x` plus a residual with reduced temporal variation; the local closed-form `lambda` estimate is enough to recover substantial low-NFE gains.
assumptions=The sampler can evaluate the current velocity field; consecutive states and velocities are available; one may estimate a piecewise-constant coefficient `lambda^(n)` from local finite differences; no retraining is required.
complete_sampling_pseudocode=
- Inputs: pretrained score or equivalent predictor; number of flow steps `N`; diffusion schedule `{sigma_tau, alpha_bar_tau}`; optional high-order integrator state from the previous step.
- FloPS base trajectory:
- Sample `x_0 ~ N(0, I)` in flow time.
- For each flow step `t_n = n / N`:
- If `t_n` is before the exact diffusion-to-flow mapping becomes valid, reuse the velocity at the earliest valid mapped time `t_min`.
- Otherwise map the flow time `t_n` to the closest diffusion time `tau` satisfying `t_n ≈ 1 / (1 + sigma_tau / alpha_bar_tau)`.
- Convert the pretrained diffusion score or prediction into the corresponding flow velocity `v_{t_n}` at the current state.
- Non-adaptive FloPS update: advance with a simple Euler step `x_{t_{n+1}} = x_{t_n} + v_{t_n} * Delta t`.
- Adaptive A-FloPS update for steps after the first:
- Estimate a local coefficient `lambda^(n)` by minimizing residual variation across consecutive steps:
- `lambda^(n) = <Delta v, Delta x> / ||Delta x||^2`, where `Delta v = v(x_{t_n}, t_n) - v(x_{t_{n-1}}, t_{n-1})` and `Delta x = x_{t_n} - x_{t_{n-1}}`.
- Define the residual velocity `h(x_t, t; lambda) = v(x_t, t) - lambda x_t`.
- Treat `lambda` as piecewise constant over the current interval and integrate the linear term exactly:
- `x_{t_{n+1}} = exp(lambda^(n) Delta t) x_{t_n} + integral exp(lambda^(n) (t_{n+1} - tau)) h(x_tau, tau; lambda^(n)) d tau`.
- Approximate the residual integral with a second-order Taylor expansion using the current residual and a backward finite-difference estimate of `dh/dt`.
- Return the terminal flow state as the generated sample.
state_variables_and_history=Current state; previous state; current velocity; previous velocity; adaptive local coefficient `lambda`; residual velocity `h`; optional high-order finite-difference cache.
nfe_accounting=The adaptive decomposition itself adds no extra model evaluations beyond the wrapped solver because `lambda` is estimated from consecutive already-computed states and velocities.
portability=direct
repo_transfer_hypothesis=The full diffusion-to-flow rewrite is too broad for a single late-step probe, but the adaptive decomposition is directly portable: on the lone `{steps_left=5}` STORK predictor step, estimate a local `lambda` from consecutive states and drifts, subtract the state-aligned linear term `lambda x`, and extrapolate only the residual innovation before reconstructing the predictor drift.
failure_or_reject_boundary=Reject any branch that rewrites the whole repo around a new flow-time parameterization or that requires wholesale scheduler replacement. The direct in-bounds residue is a localized residualized extrapolation inside the existing paper-winning tail.
citation_followups=Flow Matching; DPM-Solver++; UniPC; STORK; rectified flow; Diffusion Meets Flow Matching
status=ready

## Session Takeaway

- `S4S` is a strong negative boundary: learned time-dependent solver coefficients are genuinely useful at very low NFE, but the repo cannot promote an offline teacher-distilled coefficient search as a `sample.py`-only poster mechanism.
- `TADA` makes the augmented-dynamics lesson sharper without forcing a full momentum rewrite: what transfers cleanly is not another global latent augmentation, but the idea that late-step dynamics contain a large state-aligned linear component plus a smaller innovation term.
- `A-FloPS` contributes the missing direct formula: estimate a local scalar `lambda` from consecutive state and drift changes, subtract `lambda x`, and extrapolate the residual only. That gives a clean synthesized family which is more structural than another scalar gate yet still lives entirely inside the existing `e2379ec` late-step STORK window.

## Candidate Card

family=localized_residualized_virtual_predictor
kind=mechanism
external_anchor=A-FloPS: Accelerating Diffusion Models via Adaptive Flow Path Sampler (Jin et al., 2026); TADA: Improved Diffusion Sampling with Training-free Augmented DynAmics (Chen et al., 2025)
borrowed_mechanism=estimate a local state-aligned linear drift and extrapolate only the residual innovation, instead of extrapolating the whole late-step drift vector
synthesis_step=from the exact `e2379ec` paper base, keep the single `{steps_left=5}` STORK virtual-predictor placement but replace the raw history difference `(d_cur - prev_d_cur)` with a residualized difference `[(d_cur - lambda * x_hat) - (prev_d_cur - lambda * prev_x_hat)]`, where `lambda = <d_cur - prev_d_cur, x_hat - prev_x_hat> / ||x_hat - prev_x_hat||^2` is estimated per sample and clamped for stability; keep the `{4}` midpoint entry step, `{3}` UniPC corrector, and terminal exact-Heun pair unchanged
portability=direct
base_commit=e2379ec
active_nf_range=paper-targeted late full-step regime only; NFE 5/9/11/13 should remain in the usual dormant band because the residualized branch is inactive when `num_steps < 12`
extra_nfe=0
hypothesis=the paper-winning STORK virtual predictor may still be carrying too much of the late PF-ODE radial contraction term; subtracting a locally estimated state-aligned linear drift before extrapolation should isolate the true innovation and yield a cleaner predictor state on the single approach step
expected_signature=the proxy frontier should at least recover the dormant-band behavior of the base while improving the late full-step read; if the decomposition is right, `NFE=5` should stop softening versus the base and block-0 paper quality should remain near `1.92366` or better
ablation=if this shows life, test the same residualized virtual predictor with `prev_d_prime` instead of `prev_d_cur` as the previous-velocity term to separate residualization from raw-drift history choice
kill_condition=any clear proxy loss versus `e2379ec`, any low-NFE drift outside the normal dormant band, or any instability from the local `lambda` estimate

## Candidate Card

family=localized_residualized_virtual_predictor
kind=ablation
external_anchor=A-FloPS: Accelerating Diffusion Models via Adaptive Flow Path Sampler (Jin et al., 2026); TADA: Improved Diffusion Sampling with Training-free Augmented DynAmics (Chen et al., 2025)
borrowed_mechanism=keep the local linear-plus-residual decomposition but swap which previous velocity anchors the residual history
synthesis_step=from commit `e68bac4`, keep the localized `{steps_left=5}` residualized virtual predictor exactly as-is but replace the previous raw drift term in the residual history with the previous accepted slope `prev_d_prime`, i.e. use `[(d_cur - lambda * x_hat) - (prev_d_prime - lambda * prev_x_hat)]` while keeping the same per-sample `lambda` estimate, `{4}` midpoint entry step, `{3}` UniPC corrector, and terminal exact-Heun pair unchanged
portability=direct
base_commit=e68bac4
active_nf_range=paper-targeted late full-step regime only; NFE 5/9/11/13 should remain in the usual dormant band because only the single late virtual-predictor branch changes
extra_nfe=0
hypothesis=the near-tie proxy result suggests the residualization itself is sound, but the raw previous drift may still be slightly stale once the prior step has already been corrected; using the previous accepted slope could preserve the `NFE=9`/`NFE=11` gains while recovering the soft `NFE=5` point
expected_signature=the frontier score should improve past `2.607519` and ideally match or beat the base `2.607516`; if the family is real, the band should keep the mid-NFE gains without paying the same `NFE=5` penalty
ablation=if this loses clearly, close the residualized family rather than stacking clamp or weighting tweaks
kill_condition=any clear frontier regression versus both `e68bac4` and `e2379ec`, any new instability, or any broader low-NFE drift outside the normal dormant band

## Session Addendum

Session date: 2026-03-15
Working paper base after AMED reject: `e2379ec`
Reason for new pass: the AMED-style mean-direction family missed clearly on the proxy screen, so the next step needs a fresh literature pass before either another orthogonal family or a cleaner consolidation probe on the winning STORK mechanism.

## Paper Entry

paper_id=seeds_2023
title=SEEDS: Exponential SDE Solvers for Fast High-Quality Sampling from Diffusion Models
authors=Martin Gonzalez; Nelson Fernandez; Thuy Tran; Elies Gherbi; Hatem Hajri; Nader Masmoudi
venue_or_source=arXiv
year=2023
url=https://arxiv.org/abs/2305.14267
pdf_path=literature/pdfs/seeds_2305.14267.pdf
family=stochastic exponential integrator solvers for reverse diffusion SDEs
why_relevant=This newly added paper is a good fresh boundary for the current repo because it is one of the clearest high-quality fast-sampling papers that deliberately keeps stochasticity in the sampler rather than collapsing to a deterministic PF-ODE solver.
core_claim=One can analytically handle the linear part of reverse diffusion SDEs, compute stochastic variance terms in closed form, and build derivative-free stochastic exponential solvers that recover or exceed prior SDE quality with far fewer NFEs.
assumptions=Sampling is allowed to follow the reverse diffusion SDE rather than the deterministic PF-ODE; Gaussian noise increments are injected during inference; the solver may change variables and analytically manipulate stochastic integral terms.
complete_sampling_pseudocode=
- Inputs: pretrained diffusion model `F_theta` or data predictor; reverse time grid `{t_i}` from `T` to `0`; chosen SEEDS order and change-of-variables rule; standard Gaussian noise increments.
- Rewrite the reverse diffusion dynamics in semi-linear SDE form `dx_t = [A(t) x_t + b(t) F_theta(x_t, t)] dt + g(t) dW_t`.
- For each reverse step from `s` to `t`:
- Analytically integrate the linear part through the exponential propagator `Phi_A(t, s)`.
- Change variables so the deterministic neural-network integral becomes an exponentially weighted integral over a transformed coordinate.
- Approximate the transformed deterministic integral with low-order derivative-free terms built from one or more model evaluations depending on the chosen SEEDS order.
- Separately transform the stochastic integral and analytically compute its variance with the stochastic exponential time-differencing construction.
- Sample the corresponding Gaussian increment with that variance and add it to the deterministic update.
- Advance to the next time point and continue until the final sample is produced.
state_variables_and_history=Current sample; transformed exponential propagator factors; current model evaluation and any low-order stage evaluations; analytically computed stochastic variance terms; Gaussian noise increments.
nfe_accounting=The solver can be efficient in NFE, but it changes the sampling path to a stochastic reverse-SDE family with sampled noise increments.
portability=partial
repo_transfer_hypothesis=The only portable residue here is a negative one: exponential-integrator structure remains useful, but once stochastic variance terms are part of the mechanism the paper path is no longer the deterministic PF-ODE target used in this repo.
failure_or_reject_boundary=Reject any SEEDS-like branch that injects stochastic noise, analytically computes SDE variance terms, or otherwise changes the deterministic paper path into a reverse-SDE benchmark.
citation_followups=Exponential integrators; gDDIM; reverse diffusion SDE samplers; SETD methods
status=ready

## Paper Entry

paper_id=gddim_2023
title=GDDIM: Generalized Denoising Diffusion Implicit Models
authors=Qinsheng Zhang; Molei Tao; Yongxin Chen
venue_or_source=ICLR 2023
year=2023
url=https://arxiv.org/abs/2206.05564
pdf_path=literature/pdfs/gddim_2206.05564.pdf
family=deterministic DDIM-style accelerated sampling for general diffusion models
why_relevant=This newly added paper is useful because it explains DDIM from a numerical-analysis perspective and directly contrasts deterministic probability-flow sampling with stochastic sampling in the few-step regime.
core_claim=DDIM acceleration can be understood as a specific score approximation when solving the corresponding diffusion SDE or PF-ODE, and the deterministic probability-flow version works especially well in few-step sampling because a single score evaluation recovers more accurate directional information than the stochastic alternative.
assumptions=The model may be reparameterized appropriately for the diffusion family; deterministic PF-ODE sampling is allowed; the useful score information remains smooth along the exact trajectory.
complete_sampling_pseudocode=
- Inputs: pretrained score/noise model for a diffusion family; reverse time grid `{t_i}`; choice of deterministic (`lambda = 0`) or stochastic (`lambda > 0`) generalized DDIM.
- Express the model's reverse sampling dynamics as the generalized family `du = [F_t u - (1 + lambda^2)/2 * G_t G_t^T s_theta(u, t)] dt + lambda G_t dw`.
- For deterministic fast sampling, set `lambda = 0` to obtain the probability-flow ODE.
- At each reverse step:
- Use the current state and one model evaluation to approximate the score information needed for the next state under the DDIM-style closed-form update.
- Apply the deterministic update rule over the chosen grid to obtain the next sample state.
- Continue until the final state is reached.
- For the stochastic variant, add the corresponding Gaussian increment term controlled by `lambda`, but the paper emphasizes that the deterministic scheme is usually superior at very small step counts.
state_variables_and_history=Current sample; model output at the current step; reverse time grid; parameterization matrices/functions defining the diffusion family; optional stochastic noise increment if `lambda > 0`.
nfe_accounting=The deterministic variant is efficient and keeps a fixed score-evaluation budget, but the core lesson of the paper is explanatory rather than a new local plug-in mechanism for this repo.
portability=partial
repo_transfer_hypothesis=The useful transferable residue is that deterministic PF-ODE updates tend to dominate stochastic ones in the few-step regime, reinforcing that the repo should keep exploiting better local deterministic directions rather than adding stochasticity or another schedule-only warp.
failure_or_reject_boundary=Reject any gDDIM-inspired branch that is merely another global schedule or parameterization rewrite without a localized mechanism; the paper is more helpful here as a deterministic-selection principle than as a direct plug-in sampler edit.
citation_followups=DDIM; PF-ODE; generalized diffusion parameterizations; reverse-SDE versus ODE analysis
status=ready

## Session Takeaway

- `SEEDS` and `gDDIM` sharpen the deterministic-vs-stochastic boundary around the current paper winner: both papers explain why there is real few-step headroom in richer solvers, but they also make it clearer that this repo should stay on the deterministic PF-ODE side rather than borrowing stochastic variance terms.
- Together with `STORK`, these papers suggest the current winning mechanism is pointing in the right direction already: the local history vector used to synthesize the late predictor direction matters more than another global schedule or another state springboard.
- The cleanest next consolidation probe is therefore still inside the STORK family: keep the single `{steps_left=5}` virtual-stage construction, but replace the raw previous drift `prev_d_cur` with the accepted previous corrected slope `prev_d_prime` when estimating the virtual predictor direction.

## Candidate Card

family=localized_stork_virtual_predictor
kind=consolidation
external_anchor=STORK: Faster Diffusion And Flow Matching Sampling By Resolving Both Stiffness And Structure-Dependence (Tan et al., 2025); GDDIM: Generalized Denoising Diffusion Implicit Models (Zhang et al., 2023)
borrowed_mechanism=preserve the deterministic virtual-stage predictor idea, but use a more accepted local history vector when estimating the predictor-time slope
synthesis_step=from the exact `e2379ec` paper base, keep the same single `{steps_left=5}` STORK-inspired virtual predictor placement and replace the history difference `(d_cur - prev_d_cur)` with `(d_cur - prev_d_prime)` whenever `prev_d_prime` is available, leaving the `{4}` midpoint entry step, `{3}` UniPC corrector, and terminal exact-Heun pair unchanged
portability=direct
base_commit=e2379ec
active_nf_range=paper-targeted late full-step regime only; NFE 5/9/11/13 should remain in the usual dormant band because the branch is inactive when `num_steps < 12`
extra_nfe=0
hypothesis=the STORK family already won on paper, but the best local history vector may be the accepted previous corrected slope rather than the raw previous drift; using `prev_d_prime` could yield a cleaner virtual-stage direction on the single late approach step without broadening the family
expected_signature=the proxy frontier should stay at least as strong as `e2379ec` and ideally improve on the `2.607516` proxy reference; if promoted, paper block 0 should stay near or improve on `1.92366`
ablation=if this shows life, compare the same `{5}` placement using a gated blend of `prev_d_cur` and `prev_d_prime` rather than a hard swap
kill_condition=any low-NFE drift outside the stable band, any instability, or any proxy loss large enough to show that the accepted-slope history is weaker than the current `e2379ec` history choice

## Session Addendum

Session date: 2026-03-15
Working paper base after STORK follow-up closeout: `e2379ec`
Reason for new pass: the accepted-slope STORK consolidation probe also weakened, so the STORK family has exhausted its justified follow-ups and the next branch needs a fresh literature rotation toward a different mechanism family.

## Paper Entry

paper_id=pfode_adaptivity_2025
title=Adaptivity and Convergence of Probability Flow ODEs in Diffusion Generative Models
authors=Jiaqi Tang; Yuling Yan
venue_or_source=arXiv
year=2025
url=https://arxiv.org/abs/2501.18863
pdf_path=literature/pdfs/pfode_adaptivity_2501.18863.pdf
family=theory of PF-ODE adaptivity to intrinsic low-dimensional structure
why_relevant=This newly added paper is not a sampler recipe by itself, but it is highly relevant because it formalizes a property that the current repo keeps probing empirically: deterministic PF-ODE samplers can adapt to low-dimensional local structure and should not be judged only by ambient-dimensional intuition.
core_claim=With accurate score estimation and suitable coefficient design, probability-flow ODE samplers achieve convergence rates that depend on intrinsic rather than ambient dimension, showing that deterministic samplers can exploit low-dimensional structure of the target distribution.
assumptions=The score function is accurately estimated; the target distribution has intrinsic low-dimensional structure; the sampler follows a deterministic DDIM / probability-flow-ODE-style reverse process with suitable coefficients.
complete_sampling_pseudocode=
- Inputs: target data distribution `p_data`; learned score function `s_t`; forward noising schedule `{alpha_t, beta_t}`; total number of deterministic reverse iterations `T`.
- Define the forward diffusion process and its learned score approximation over the schedule.
- Initialize the reverse process at Gaussian noise `Y_T`.
- For each reverse step `t = T ... 1`:
- Apply the deterministic probability-flow-ODE update `Y_{t-1} = alpha_t^{-1/2} * (Y_t + eta_t * s_t(Y_t))`, with the DDIM-style coefficient choice `eta_t`.
- Continue until `Y_0` is produced.
- Analyze convergence by bounding the total-variation distance between the reverse iterate distribution and the target distribution in terms of intrinsic dimension, score error, and Jacobian error.
state_variables_and_history=Current deterministic reverse iterate `Y_t`; learned score `s_t`; DDIM-style coefficients `eta_t`; score/Jacobian error quantities in the analysis.
nfe_accounting=The paper analyzes a deterministic PF-ODE sampler under a fixed iteration budget; it does not propose extra evaluations or a new practical stage structure.
portability=partial
repo_transfer_hypothesis=The portable lesson is that a deterministic sampler can benefit from local structure-adaptive behavior without changing the benchmark itself. In this repo, that points toward local per-sample solver allocation rather than another global schedule or stochastic family.
failure_or_reject_boundary=Reject any use that tries to treat the paper as a concrete new solver formula; it is primarily a theoretical justification for adaptive deterministic behavior, not a drop-in sampler implementation.
citation_followups=DDIM; PF-ODE theory; intrinsic-dimension analyses; Jacobian-error control papers
status=ready

## Paper Entry

paper_id=pfode_minimax_2025
title=Minimax Optimality of the Probability Flow ODE for Diffusion Models
authors=Changxiao Cai; Gen Li
venue_or_source=arXiv
year=2025
url=https://arxiv.org/abs/2503.09583
pdf_path=literature/pdfs/pfode_minimax_2503.09583.pdf
family=end-to-end deterministic PF-ODE theory with smooth score and Jacobian control
why_relevant=This newly added theory paper is valuable because it reinforces a practical constraint seen in this repo: deterministic ODE samplers care not only about score error but also about the smoothness and Jacobian behavior of the chosen direction field.
core_claim=Under a smooth regularized score estimator that controls both score and mean Jacobian error, the resulting deterministic probability-flow-ODE sampler can achieve near-minimax total-variation guarantees without strong structural assumptions on the target distribution.
assumptions=The score estimator is smooth enough that Jacobian error is controlled; the deterministic sampler follows a PF-ODE update; convergence is measured end-to-end rather than only conditionally on an oracle score.
complete_sampling_pseudocode=
- Inputs: training data from the target distribution; smooth score estimator `s_t`; deterministic PF-ODE reverse update coefficients.
- Train or construct a score estimator that controls both `L2` score error and mean Jacobian error.
- Initialize the reverse process from Gaussian noise.
- For each reverse step:
- Apply the deterministic PF-ODE / DDIM-style update using the smooth score estimate at the current iterate.
- Propagate the deterministic iterate to the final sample.
- Bound the final sampling error by jointly tracking score-estimation error, Jacobian error, initialization bias, and discretization effects.
state_variables_and_history=Current deterministic reverse iterate; smooth score estimate; Jacobian of the score estimate; reverse coefficients; initialization and discretization error terms in the analysis.
nfe_accounting=The paper is theoretical and keeps the deterministic PF-ODE iteration budget fixed; it does not prescribe extra model evaluations.
portability=partial
repo_transfer_hypothesis=The useful residue is that deterministic sampler edits should prefer smooth local deformations and adaptive allocations over abrupt branch replacements or stochastic perturbations. That supports trying a smooth local allocation between existing predictor rules rather than inventing a new hard branch.
failure_or_reject_boundary=Reject any reading that turns this into a training procedure for smooth score estimators; under the repo contract, only the deterministic local-allocation lesson is portable.
citation_followups=PF-ODE theory; DDIM; Jacobian-aware score estimation; minimax sampling theory
status=ready

## Paper Entry

paper_id=pfode_weak_logconcavity_2025
title=Non-asymptotic error bounds for probability flow ODEs under weak log-concavity
authors=Gitte Kremling; Francesco Iafrate; Mahsa Taheri; Johannes Lederer
venue_or_source=arXiv
year=2025
url=https://arxiv.org/abs/2510.17608
pdf_path=literature/pdfs/pfode_weak_logconcavity_2510.17608.pdf
family=non-asymptotic PF-ODE convergence with explicit discretization effects
why_relevant=This newly added theory paper is useful here because it explicitly tracks discretization error and even discusses exponential-integrator discretization under more realistic distributional assumptions, which connects directly to the repo's step-local mechanism work.
core_claim=Probability-flow ODE samplers admit explicit non-asymptotic error bounds under weak log-concavity and Lipschitz score assumptions, with initialization, score error, and discretization all visible in the final bound; these rates can guide practical step-size choices and solver design.
assumptions=The target distribution satisfies weak log-concavity-type assumptions; the score function is Lipschitz; the PF-ODE is discretized, potentially with an exponential-integrator scheme.
complete_sampling_pseudocode=
- Inputs: forward SDE coefficients `f(t), g(t)`; learned score function; deterministic PF-ODE discretization parameters; total integration horizon.
- Define the forward diffusion process and the corresponding reverse probability-flow ODE.
- Initialize the reverse ODE from a chosen starting distribution near the terminal Gaussian.
- Discretize the PF-ODE with a selected step size and solver scheme, including exponential-integrator variants covered by the analysis.
- At each deterministic reverse step:
- Evaluate the learned score at the current iterate.
- Advance the sample using the chosen discretized PF-ODE rule.
- Track initialization, discretization, and score-approximation errors through the theoretical bound.
state_variables_and_history=Current deterministic reverse iterate; learned score evaluation; step-size / discretization parameters; propagated error terms in the analysis.
nfe_accounting=The paper does not change model-call accounting; it analyzes how discretization quality affects deterministic PF-ODE sampling under a fixed iteration budget.
portability=partial
repo_transfer_hypothesis=The portable residue is that deterministic PF-ODE solver design should expose discretization quality smoothly and locally. That again favors a soft per-sample allocation between two existing predictor rules over another hard step-law rewrite.
failure_or_reject_boundary=Reject any attempt to turn the paper into a global schedule rewrite or distribution-assumption-dependent benchmark change; the practical transfer is only the preference for smooth local allocation under fixed deterministic NFEs.
citation_followups=PF-ODE theory; exponential integrators; weak log-concavity analyses; regime-shifting discussions
status=ready

## Session Takeaway

- The three fresh PF-ODE theory papers all point to the same practical residue: deterministic samplers benefit from local structure-adaptive behavior, but that behavior should be smooth and local rather than a hard global family swap.
- Together with the existing `sdm_2026` paper entry, the cleanest next family is a per-sample adaptive solver-allocation probe on top of the `e2379ec` paper winner: keep the current STORK virtual predictor available, keep the original extrapolation rule available, and let a local gate decide how much of each to use on the single late `{5}` step.
- This is meaningfully different from the earlier curvature-gated exact-Heun miss: the new family does not promote a whole step to a different solver, it only allocates between two already-tested predictor directions while leaving the downstream midpoint-plus-UniPC tail untouched.

## Candidate Card

family=localized_adaptive_predictor_allocation
kind=mechanism
external_anchor=Formalizing the Sampling Design Space of Diffusion-Based Generative Models via Adaptive Solvers and Wasserstein-Bounded Timesteps (Jo and Choi, 2026); Adaptivity and Convergence of Probability Flow ODEs in Diffusion Generative Models (Tang and Yan, 2025); Minimax Optimality of the Probability Flow ODE for Diffusion Models (Cai and Li, 2025)
borrowed_mechanism=allocate solver behavior smoothly and locally using a per-sample adaptivity signal instead of committing the whole step to one predictor rule
synthesis_step=from the exact `e2379ec` paper base, keep the single `{steps_left=5}` STORK virtual predictor placement but replace the hard choice of the virtual predictor with a smooth per-sample blend between the original extrapolation predictor and the STORK virtual predictor, using the existing `growth_gate` to weight the allocation on that step only; keep the `{4}` midpoint entry step, `{3}` UniPC corrector, and terminal exact-Heun pair unchanged
portability=direct
base_commit=e2379ec
active_nf_range=paper-targeted late full-step regime only; NFE 5/9/11/13 should remain in the usual dormant band because the blend branch is inactive when `num_steps < 12`
extra_nfe=0
hypothesis=the paper-winning STORK predictor may still be over-applied on some samples, while the original extrapolation remains better on others; a smooth local allocation using the existing `growth_gate` could preserve the structural win while reducing the proxy-side overreach that shows up in the same-family misses
expected_signature=the proxy frontier should beat the recent STORK follow-up misses and ideally recover to or improve on the `e2379ec` reference `2.607516`; if promoted, paper block 0 should stay near or improve on `1.92366`
ablation=if this shows life, compare the same allocation using `1 - growth_gate` versus `growth_gate` as the virtual-predictor weight so we can verify the allocation polarity
kill_condition=any low-NFE drift outside the stable band, any instability, or any clear proxy loss that shows the allocation family is weaker than the hard `e2379ec` winner

## Candidate Card

family=localized_pfdiff_springboard_predictor
kind=ablation
external_anchor=PFDiff: Training-Free Acceleration of Diffusion Models Combining Past and Future Scores (Wang et al., 2025); FSampler: Training-Free Acceleration of Diffusion Sampling via Epsilon Extrapolation (Vladimir, 2025)
borrowed_mechanism=keep the same single-step springboard-state family but change which cached past signal defines the springboard, testing raw drift reuse against accepted-slope reuse
synthesis_step=from the exact `e2379ec` base and the just-screened `1082d40` springboard family, keep the same single `{steps_left=5}` springboard placement and replace `prev_d_prime` with the raw previous drift `prev_d_cur` in the predictor-state construction `x_spring = x_hat + alpha * h * prev_d_cur`, leaving the `{4}` midpoint entry step, `{3}` UniPC corrector, and terminal exact-Heun pair unchanged
portability=direct
base_commit=e2379ec
active_nf_range=paper-targeted late full-step regime only; NFE 5/9/11/13 should remain in the usual dormant band because the springboard branch is inactive when `num_steps < 12`
extra_nfe=0
hypothesis=the near-tie miss of `1082d40` suggests that a late springboard state may be directionally sound, but the accepted predictor slope could be slightly over-advanced; using the raw previous drift may yield a cleaner one-step springboard into the winning midpoint-plus-UniPC tail
expected_signature=the proxy frontier should beat `1082d40` and ideally return to or improve on the `e2379ec` proxy reference; if it weakens again, the springboard-state family should be closed and treated as inferior to the STORK virtual-drift family
ablation=if this also weakens, rotate away from springboard-state variants instead of testing more cached-signal choices
kill_condition=any low-NFE drift outside the stable band, any instability, or any paper block-0 signal that would clearly trail the `e2379ec` base

## Session Addendum

Session date: 2026-03-15
Working paper base after springboard-family closeout: `e2379ec`
Reason for new pass: the PFDiff-style springboard family produced two consecutive proxy misses, so `program.md` requires a fresh literature rotation before another family change.

## Paper Entry

paper_id=amed_solver_2024
title=Fast ODE-based Sampling for Diffusion Models in Around 5 Steps
authors=Zhenyu Zhou; Defang Chen; Can Wang; Chun Chen
venue_or_source=arXiv
year=2024
url=https://arxiv.org/abs/2312.00094
pdf_path=literature/pdfs/amed_solver_2312.00094.pdf
family=learned approximate mean-direction single-step solver and plugin
why_relevant=This newly added paper is the cleanest fresh source for a geometric "mean direction" family. It argues that fast-sampling trajectories approximately live in a two-dimensional subspace and that the useful update direction is a mean direction inside that local plane rather than a purely local truncation formula.
core_claim=At extremely low NFE, high-order ODE solvers still suffer from truncation error; one can instead learn an intermediate evaluation location and scaling factor that directly approximate the mean direction of the PF-ODE integral, and the same idea can be plugged into existing ODE samplers.
assumptions=A shallow predictor can be trained by distillation against teacher trajectories; each sampling path is approximately low-dimensional; the solver may choose an intermediate time `s_n` and a scaling factor `c_n` for each step.
complete_sampling_pseudocode=
- Inputs: pretrained diffusion model in PF-ODE form; N-step schedule `{t_n}`; learned AMED predictor `g_phi`; optional base ODE solver to receive the AMED plugin.
- Teacher-data stage:
- Generate dense teacher trajectories `{y_{t_n}}` with a strong solver.
- For each student step from `t_{n+1}` to `t_n`, train `g_phi` to predict an intermediate time `s_n in (t_n, t_{n+1})` and a scaling factor `c_n`.
- AMED single-step inference:
- Query `g_phi` on the current student state and nearby teacher/student context to obtain `(s_n, c_n)`.
- Evaluate the diffusion model at the intermediate state `x_{s_n}` and time `s_n`.
- Update the sample with the learned mean-direction rule `x_{t_n} = x_{t_{n+1}} + c_n * (t_n - t_{n+1}) * epsilon_theta(x_{s_n}, s_n)`.
- AMED plugin mode:
- Replace the heuristic intermediate location and scale inside an existing ODE solver (for example generalized DPM-Solver-2) with the learned `(s_n, c_n)`.
- Continue until the final sample is reached.
state_variables_and_history=Current sample; learned AMED predictor `g_phi`; intermediate time `s_n`; scaling factor `c_n`; optional teacher trajectory during training; optional base-solver history for plugin mode.
nfe_accounting=The deployed solver can preserve the NFE budget of the wrapped ODE solver, but the method fundamentally depends on a trained predictor obtained by distillation against teacher trajectories.
portability=partial
repo_transfer_hypothesis=The faithful learned AMED plugin is out of scope, but the paper leaves one portable residue: if the local update direction is what matters, a deterministic norm-preserving mean direction inside the span of recent real drifts could be tested on a single late step without any learned predictor.
failure_or_reject_boundary=Reject any direct AMED branch that introduces a trained predictor for `s_n` or `c_n`, teacher-generated trajectory assets, or global low-NFE-path changes. The only in-bounds transfer is a tiny deterministic mean-direction heuristic on the paper-targeted late step.
citation_followups=DPM-Solver-2; Heun; EDM; DEIS; distillation-based fast samplers
status=ready

## Paper Entry

paper_id=sa_solver_2025
title=SA-Solver: Stochastic Adams Solver for Fast Sampling of Diffusion Models
authors=Shuchen Xue; Mingyang Yi; Weijian Luo; Shifeng Zhang; Jiacheng Sun; Zhenguo Li; Zhi-Ming Ma
venue_or_source=arXiv
year=2025
url=https://arxiv.org/abs/2309.05019
pdf_path=literature/pdfs/sa_solver_2309.05019.pdf
family=variance-controlled stochastic Adams solver for diffusion SDEs
why_relevant=This newly added paper is a useful reject boundary for the current repo because it shows a different route to few-step quality through controlled stochasticity and Adams-style SDE integration rather than through deterministic PF-ODE updates.
core_claim=By solving a family of variance-controlled diffusion SDEs with a stochastic Adams integrator, one can obtain higher-quality or more diverse samples than ODE samplers under suitable NFEs, including strong FID at moderate step counts.
assumptions=Sampling is allowed to inject controlled noise through a time-varying `tau(t)`; the solver is free to operate on the diffusion SDE rather than the deterministic PF-ODE; the model is expressed in data-prediction form for the solver derivation.
complete_sampling_pseudocode=
- Inputs: pretrained diffusion model in data-prediction form; reverse schedule `{t_i}`; noise-scale function `tau(t)` defining the chosen diffusion SDE from the shared marginal family.
- Rewrite the sampling dynamics as a variance-controlled diffusion SDE with drift and diffusion terms determined by `tau(t)`.
- Change variables to the log-SNR coordinate and derive the exponentially weighted stochastic integral.
- Maintain an Adams-style history of previous model evaluations in the transformed coordinates.
- For each reverse step:
- Combine the deterministic Adams predictor term from recent history.
- Add the analytically derived stochastic variance term corresponding to `tau(t)`.
- Advance the sample to the next time point and continue until the final sample is produced.
state_variables_and_history=Current sample; previous transformed drifts or data-prediction evaluations; stochastic noise increments; chosen `tau(t)` schedule; Adams history buffer.
nfe_accounting=The method can be efficient in NFE, but it changes the sampling problem from deterministic PF-ODE integration to stochastic SDE integration with injected noise.
portability=partial
repo_transfer_hypothesis=The only useful lesson here is negative: controlled stochasticity can help at few steps, but this repo's authoritative paper path is deterministic and should not be confounded with an SDE-family change while chasing a simple poster mechanism.
failure_or_reject_boundary=Reject any SA-Solver-like branch that adds stochastic noise, depends on a learned or hand-tuned `tau(t)` noise law, or changes the deterministic paper path into an SDE benchmark.
citation_followups=DPM-Solver++; UniPC; stochastic Adams methods; diffusion SDE versus ODE comparisons
status=ready

## Session Takeaway

- `AMED-Solver` opens a more interesting deterministic family than the just-closed springboard branch: the paper's real geometric residue is not the learned plugin itself, but the idea that the useful late-step update may be a norm-preserving mean direction inside the recent local drift plane.
- `SA-Solver` is a clear boundary for this repo: stochastic Adams improvements change the sampling problem itself, so they are not the next clean mechanism under the deterministic paper protocol.
- The new orthogonal probe should therefore stay deterministic, keep the `e2379ec` paper base intact everywhere except the single `{steps_left=5}` approach step, and test a tiny AMED-style mean-direction heuristic rather than another state springboard or schedule warp.

## Candidate Card

family=localized_amed_mean_direction
kind=mechanism
external_anchor=Fast ODE-based Sampling for Diffusion Models in Around 5 Steps (Zhou et al., 2024)
borrowed_mechanism=replace the late predictor update direction with a deterministic norm-preserving mean direction built from the local drift plane, approximating the paper's learned mean-direction idea without any trained predictor
synthesis_step=from the exact `e2379ec` paper base, disable the STORK virtual-drift branch on the single `{steps_left=5}` approach step and instead set `predictor_d` to the norm-preserving bisector of `prev_d_cur` and `d_cur`, using the current drift norm and the normalized sum direction; keep the `{4}` midpoint entry step, `{3}` UniPC corrector, and terminal exact-Heun pair unchanged
portability=direct
base_commit=e2379ec
active_nf_range=paper-targeted late full-step regime only; NFE 5/9/11/13 should remain in the usual dormant band because the branch is inactive when `num_steps < 12`
extra_nfe=0
hypothesis=the remaining full-step error may lie in the predictor direction rather than the predictor state; a norm-preserving local mean direction could approximate AMED's learned mean-direction benefit on the one late approach step without learned coefficients or extra evaluations
expected_signature=the proxy frontier should remain in the stable dormant band; if promoted, paper block 0 should stay near or improve on the `e2379ec` base `1.92366`, while a clear proxy loss would reject the mean-direction family quickly
ablation=if this family shows life, compare the same `{5}` placement using the accepted previous slope `prev_d_prime` in the mean-direction span instead of `prev_d_cur`
kill_condition=any low-NFE drift outside the stable band, any instability, or any paper block-0 loss that clearly trails the `e2379ec` base
