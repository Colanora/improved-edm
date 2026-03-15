# Paper Note: DyWeight: Dynamic Gradient Weighting for Few-Step Diffusion Sampling

paper_id=dyweight_2026
current_note_from=pass_05
pass_refs=pass_05

## Canonical Note


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
