# Paper Note: Image Diffusion Preview with Consistency Solver

paper_id=consistency_solver_2025
current_note_from=pass_06
pass_refs=pass_06

## Canonical Note


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
