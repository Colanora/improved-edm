# Paper Note: Accelerating Diffusion Sampling via Exploiting Local Transition Coherence

paper_id=ltc_accel_2025
current_note_from=pass_02
pass_refs=pass_02

## Canonical Note


paper_id=ltc_accel_2025
title=Accelerating Diffusion Sampling via Exploiting Local Transition Coherence
authors=Shangwen Zhu; Han Zhang; Zhantao Yang; Qianyu Peng; Zhao Pu; Huangji Wang; Fan Cheng
venue_or_source=ICCV 2025
year=2025
url=https://arxiv.org/abs/2503.09675
pdf_path=literature/pdfs/ltc_accel_2503.09675.pdf
family=transition-operator reuse / step-skipping acceleration
why_relevant=This is a recent independently discovered training-free paper that initially looks relevant because it exploits local transition structure without network-specific assumptions. It is useful mainly as a reject boundary for this repo's frozen NFE accounting.
core_claim=Adjacent transition operators in diffusion sampling are strongly coherent over a sizable interval, so one can estimate the current transition from neighboring steps and skip explicit denoiser evaluations to accelerate generation.
assumptions=The method identifies an acceleration interval where adjacent transition directions have small angle; it approximates the current transition by a scaled neighboring transition and locally searches a weight parameter `w_g`; practical benefit comes from reducing the number of expensive denoiser evaluations.
complete_sampling_pseudocode=
- Inputs: baseline diffusion sampler with transitions `Delta x_{t+1,t}`, acceleration interval `[a, b]`, denoising progress function `phi(t)`.
- Detect or predefine an interval where the angle between adjacent transition operators is below a threshold.
- For a skipped step `t`, approximate the current transition by reusing the next-step transition:
- `x_t^* = x_{t+1} + w_g * gamma * Delta x_{t+2,t+1}`.
- Set `gamma = (phi(t) - phi(t+1)) / (phi(t+1) - phi(t+2))`.
- Estimate `w_g` by minimizing the discrepancy between the approximated transition and the true transition, with an optional local search across the full acceleration interval.
- Replace true denoiser evaluations inside the acceleration interval with the approximated transitions.
- Outside the interval, run the original sampler unchanged.
state_variables_and_history=Current and adjacent transition operators; acceleration interval; progress ratio `gamma`; locally searched weight `w_g`.
nfe_accounting=The point of the method is to skip denoiser evaluations and gain wall-clock speed, so it changes the effective computation contract even when nominal step counts are reported.
portability=incompatible
repo_transfer_hypothesis=The only portable lesson is that late-step transition directions can be highly redundant, but the actual LTC mechanism is out of scope here because it achieves its benefit by skipping explicit model evaluations instead of spending the fixed NFE budget more intelligently.
failure_or_reject_boundary=Reject direct use because this repo's contract is fixed-NFE sampler research, not step-skipping acceleration. Any faithful LTC adaptation would either change true NFE accounting or require a different benchmark contract.
citation_followups=DeepCache; Align Your Steps; DDIM; DPM-Solver
status=ready
