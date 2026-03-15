# Paper Note: Non-asymptotic error bounds for probability flow ODEs under weak log-concavity

paper_id=pfode_weak_logconcavity_2025
current_note_from=pass_10
pass_refs=pass_10

## Canonical Note


paper_id=pfode_weak_logconcavity_2025
title=Non-asymptotic error bounds for probability flow ODEs under weak log-concavity
authors=Gitte Kremling; Francesco Iafrate; Mahsa Taheri; Johannes Lederer
venue_or_source=arXiv
year=2025
url=https://arxiv.org/abs/2510.17608
pdf_path=literature/pdfs/pfode_weak_logconcavity_2510.17608.pdf
family=non-asymptotic PF-ODE convergence with explicit discretization effects
why_relevant=This newly added theory paper is useful here because it explicitly tracks discretization error and even discusses exponential-integrator discretization under more realistic distributional assumptions, which connects directly to the repo's step-local mechanism work.
core_claim=Probability-flow ODE samplers admit explicit non-asymptotic error bounds under weak log-concavity and Lipschitz score assumptions, with initialization, score error, and discretization all visible in the final bound; these rates can guide practical step-size choices and solver design.
assumptions=The target distribution satisfies weak log-concavity-type assumptions; the score function is Lipschitz; the PF-ODE is discretized, potentially with an exponential-integrator scheme.
complete_sampling_pseudocode=
- Inputs: forward SDE coefficients `f(t), g(t)`; learned score function; deterministic PF-ODE discretization parameters; total integration horizon.
- Define the forward diffusion process and the corresponding reverse probability-flow ODE.
- Initialize the reverse ODE from a chosen starting distribution near the terminal Gaussian.
- Discretize the PF-ODE with a selected step size and solver scheme, including exponential-integrator variants covered by the analysis.
- At each deterministic reverse step:
- Evaluate the learned score at the current iterate.
- Advance the sample using the chosen discretized PF-ODE rule.
- Track initialization, discretization, and score-approximation errors through the theoretical bound.
state_variables_and_history=Current deterministic reverse iterate; learned score evaluation; step-size / discretization parameters; propagated error terms in the analysis.
nfe_accounting=The paper does not change model-call accounting; it analyzes how discretization quality affects deterministic PF-ODE sampling under a fixed iteration budget.
portability=partial
repo_transfer_hypothesis=The portable residue is that deterministic PF-ODE solver design should expose discretization quality smoothly and locally. That again favors a soft per-sample allocation between two existing predictor rules over another hard step-law rewrite.
failure_or_reject_boundary=Reject any attempt to turn the paper into a global schedule rewrite or distribution-assumption-dependent benchmark change; the practical transfer is only the preference for smooth local allocation under fixed deterministic NFEs.
citation_followups=PF-ODE theory; exponential integrators; weak log-concavity analyses; regime-shifting discussions
status=ready
