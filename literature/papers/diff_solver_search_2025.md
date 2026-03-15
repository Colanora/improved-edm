# Paper Note: Differentiable Solver Search for Fast Diffusion Sampling

paper_id=diff_solver_search_2025
current_note_from=pass_06
pass_refs=pass_06

## Canonical Note


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
