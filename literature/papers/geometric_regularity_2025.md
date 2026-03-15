# Paper Note: Geometric Regularity in Deterministic Sampling Dynamics of Diffusion-based Generative Models

paper_id=geometric_regularity_2025
current_note_from=pass_01
pass_refs=pass_01

## Canonical Note


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
