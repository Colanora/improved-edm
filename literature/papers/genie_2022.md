# Paper Note: GENIE: Higher-Order Denoising Diffusion Solvers

paper_id=genie_2022
current_note_from=pass_00
pass_refs=pass_00

## Canonical Note


paper_id=genie_2022  
title=GENIE: Higher-Order Denoising Diffusion Solvers  
authors=Tim Dockhorn; Arash Vahdat; Karsten Kreis  
venue_or_source=arXiv 2022  
year=2022  
url=https://arxiv.org/abs/2210.05475  
pdf_path=literature/pdfs/genie_2210.05475.pdf  
family=higher-order Taylor solver with distilled higher-order score head  
why_relevant=This paper is useful mainly as a reject boundary. It is a clean example of a solver idea that is training-free only in the sampling update but still needs an extra trained head to be practical.  
core_claim=GENIE accelerates diffusion ODE sampling by applying a second-order truncated Taylor method to the DDIM ODE and learning a small additional network head that predicts the required higher-order Jacobian-vector-product terms efficiently during synthesis.  
assumptions=The method can obtain higher-order score terms by automatic differentiation and then distill them into an auxiliary head attached to the score network; practical synthesis depends on that extra learned module.  
complete_sampling_pseudocode=
- Train the base first-order score model as usual.
- Compute the higher-order derivative terms of the DDIM ODE using automatic differentiation / Jacobian-vector products.
- Distill those higher-order terms into a small auxiliary prediction head attached to the score network.
- During sampling, evaluate both the base score model and the auxiliary head at each step.
- Apply the second-order truncated Taylor update using the predicted higher-order derivative term.
- Repeat until the final sample is reached.
state_variables_and_history=Current sample; base score model output; distilled higher-order derivative head output; DDIM ODE step size.  
nfe_accounting=Sampling uses few solver steps, but the approach requires training an additional head and therefore is not a pure sample.py-only modification.  
portability=incompatible  
repo_transfer_hypothesis=The only transferable lesson is that higher-order local curvature matters near the end of the trajectory, but the actual GENIE mechanism is outside this repo because it needs an extra trained module.  
failure_or_reject_boundary=Reject direct use because program.md forbids added trainable parameters and extra model heads.  
citation_followups=DDIM; PNDM; higher-order Itô-Taylor solvers  
status=ready
