# Paper Note: GDDIM: Generalized Denoising Diffusion Implicit Models

paper_id=gddim_2023
current_note_from=pass_09
pass_refs=pass_09

## Canonical Note


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
