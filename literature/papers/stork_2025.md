# Paper Note: STORK: Faster Diffusion And Flow Matching Sampling By Resolving Both Stiffness And Structure-Dependence

paper_id=stork_2025
current_note_from=pass_05
pass_refs=pass_05

## Canonical Note


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
