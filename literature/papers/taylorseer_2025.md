# Paper Note: From Reusing to Forecasting: Accelerating Diffusion Models with TaylorSeers

paper_id=taylorseer_2025
current_note_from=pass_03
pass_refs=pass_03

## Canonical Note


paper_id=taylorseer_2025
title=From Reusing to Forecasting: Accelerating Diffusion Models with TaylorSeers
authors=Jiacheng Liu; Chang Zou; Yuanhuiyi Lyu; Junjie Chen; Linfeng Zhang
venue_or_source=arXiv
year=2025
url=https://arxiv.org/abs/2503.06923
pdf_path=literature/pdfs/taylorseer_2503.06923.pdf
family=feature-cache forecasting inside diffusion transformers
why_relevant=This is a recent independently discovered acceleration paper that is useful mainly as a reject boundary. Its "forecast rather than reuse" idea rhymes with extrapolation, but the actual mechanism lives inside the model's hidden-feature cache rather than at the sampler update level.
core_claim=Instead of reusing cached hidden features from earlier timesteps, predict future transformer features with Taylor-series finite differences; this preserves quality at much higher acceleration ratios than naive cache reuse.
assumptions=The diffusion model exposes internal layer features across timesteps; those features evolve smoothly enough for finite-difference forecasting; inference can skip large parts of transformer computation by substituting forecast features.
complete_sampling_pseudocode=
- Inputs: diffusion transformer with cacheable block features, cache interval `N`, Taylor order `m`.
- At fully computed timesteps, cache each layer feature and its finite differences up to order `m`.
- For skipped intermediate timesteps, predict each feature with the Taylor expansion `F_pred(t-k) = F(t) + sum_i Delta^i F(t) * (-k)^i / (i! * N^i)`.
- Feed the forecast features through the remaining computation instead of recomputing the expensive layers.
- Periodically refresh the cache with a full model evaluation and update the finite-difference stack.
- Continue sampling with the accelerated internal model execution.
state_variables_and_history=Per-layer cached features; finite-difference feature stack; cache interval; Taylor order; skipped-step counters.
nfe_accounting=The paper accelerates inference by reusing or forecasting internal features and skipping substantial model computation, not by changing a fixed sampler mechanism under an identical denoiser-call contract.
portability=incompatible
repo_transfer_hypothesis=The portable lesson is only conceptual: forecasting can outperform raw reuse when a state trajectory is smooth. The actual TaylorSeer mechanism is incompatible because this repo exposes only the sampler surface, not model internals or feature caches.
failure_or_reject_boundary=Reject direct use because it requires instrumenting hidden transformer features and caching internal activations, which is far outside the `sample.py`-only contract.
citation_followups=FORA; ToCa; TeaCache; DiT acceleration papers
status=ready
