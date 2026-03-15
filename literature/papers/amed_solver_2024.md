# Paper Note: Fast ODE-based Sampling for Diffusion Models in Around 5 Steps

paper_id=amed_solver_2024
current_note_from=pass_11
pass_refs=pass_11

## Canonical Note


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
