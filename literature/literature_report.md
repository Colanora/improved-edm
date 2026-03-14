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
