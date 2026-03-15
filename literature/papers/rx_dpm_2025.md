# Paper Note: Enhanced Diffusion Sampling via Extrapolation with Multiple ODE Solutions

paper_id=rx_dpm_2025
current_note_from=pass_03
pass_refs=pass_03

## Canonical Note


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
