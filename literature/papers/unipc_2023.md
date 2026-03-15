# Paper Note: UniPC: A Unified Predictor-Corrector Framework for Fast Sampling of Diffusion Models

paper_id=unipc_2023
current_note_from=pass_00
pass_refs=pass_00

## Canonical Note


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
