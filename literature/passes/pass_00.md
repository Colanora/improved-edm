# Literature Pass pass_00

pass_id=pass_00
session_date=2026-03-14
working_paper_base=8f3ebc2
trigger=initial flat literature block from the pre-hierarchy report
paper_refs=unipc_2023, pndm_2022, pfdiff_2025, dc_solver_2024, dualfast_2025, dpm_solverpp_2022, dpm_solver_v3_2023, tada_2025, aflops_2025, era_solver_2023, genie_2022
candidate_families=localized_multistep_predictor_scale, localized_unipc_preterminal_corrector, localized_dualfast_preunipc_compensation, localized_dcsolver_buffer_compensation, localized_xtheta_multistep_approach, localized_era_basis_selection

> Note: this file preserves the large pre-hierarchy block from the original flat report. It contains multiple early paper readings and candidate cards that were all stored before explicit pass addenda were introduced.

## Consulted Papers

- [`unipc_2023`](../papers/unipc_2023.md)
- [`pndm_2022`](../papers/pndm_2022.md)
- [`pfdiff_2025`](../papers/pfdiff_2025.md)
- [`dc_solver_2024`](../papers/dc_solver_2024.md)
- [`dualfast_2025`](../papers/dualfast_2025.md)
- [`dpm_solverpp_2022`](../papers/dpm_solverpp_2022.md)
- [`dpm_solver_v3_2023`](../papers/dpm_solver_v3_2023.md)
- [`tada_2025`](../papers/tada_2025.md)
- [`aflops_2025`](../papers/aflops_2025.md)
- [`era_solver_2023`](../papers/era_solver_2023.md)
- [`genie_2022`](../papers/genie_2022.md)

## Session Takeaway


- Ready direct anchors for `sample.py`-only work: `UniPC`, `PNDM`, `DualFast`.
- Ready partial anchors that suggest synthesis but not direct reproduction: `PFDiff`, `DC-Solver`.
- Main portability lesson: the repo already rewards mechanisms that are dormant on NFE 5/9/11/13 and only act on late standard-regime, non-terminal steps. The literature backs localized history-based refinement more strongly than global schedule rewrites or learned/offline compensation.
- Synthesized next-family target if the current predictor-scale screen misses: a localized UniPC-style late corrector that reuses buffered history only on the non-terminal standard-regime window immediately before the terminal exact-Heun pair.


## Candidate Card


family=localized_multistep_predictor_scale
kind=tuning
external_anchor=Pseudo Numerical Methods for Diffusion Models on Manifolds (Liu et al., 2022); UniPC (Zhao et al., 2023)
borrowed_mechanism=late Adams-Bashforth-style predictor extrapolation using buffered score history on already-stable non-terminal steps
synthesis_step=one last scale-boundary probe from the `8f3ebc2` paper base: raise the localized predictor extrapolation scale from `0.75` to `1.0` without changing activation timing, terminal handling, or low-NFE behavior
portability=direct
base_commit=8f3ebc2
active_nf_range=late standard/paper regime; NFE 5/9/11/13 should stay unchanged and NFE 35 is the local screen
extra_nfe=0
hypothesis=a slightly stronger late extrapolation sharpens entry into the terminal exact-Heun pair and improves `fid_N35` and paper block 0 without reopening the block-1 softening too much
expected_signature=`fid_N35 < 6.7555` with unchanged NFE 5/9/11/13, and if promoted, a paper block-0 result below `1.95605`
ablation=if this screen misses, restore `8f3ebc2` and rotate to the synthesized localized UniPC-style late-corrector family rather than taking another predictor-only scale step
kill_condition=any low-NFE frontier drift, any `fid_N35` regression versus `8f3ebc2`, or any obvious destabilization of the terminal exact-Heun window


## Candidate Card


family=localized_unipc_preterminal_corrector
kind=mechanism
external_anchor=UniPC (Zhao et al., 2023); DC-Solver (Zhao et al., 2024)
borrowed_mechanism=use the same second model evaluation as a localized corrector that combines the current drift, endpoint drift, and one previous-drift history term
synthesis_step=apply a zero-extra-NFE UniPC-style corrector only on the two pre-terminal standard-regime steps immediately before the existing terminal exact-Heun pair, while restoring the predictor extrapolation scale to the `8f3ebc2` base value of `0.75`
portability=direct
base_commit=8f3ebc2
active_nf_range=paper-targeted late full-step regime only; NFE 5/9/11/13 should remain unchanged because the branch is inactive when `num_steps < 12`
extra_nfe=0
hypothesis=the current base may still be entering the terminal exact-Heun pair with the wrong local curvature on the two preceding steps; replacing only those steps with a localized UniPC-style endpoint/history corrector should improve `fid_N35` without reopening the wider exact-Heun-window failure mode
expected_signature=`fid_N35 < 6.7555` with unchanged NFE 5/9/11/13; if promoted, block 0 should improve beyond `1.95605`
ablation=if this candidate wins, compare the localized corrector against a same-window endpoint-Heun-only version to isolate whether the history term itself matters
kill_condition=any `fid_N35` regression, or any sign that the wider localized corrector behaves like the already-failed widened exact-Heun window rather than a distinct history-aware mechanism


## Candidate Card


family=localized_unipc_preterminal_corrector
kind=ablation
external_anchor=UniPC (Zhao et al., 2023)
borrowed_mechanism=remove the previous-drift history term while keeping the same pre-terminal endpoint evaluation window
synthesis_step=from `5e43179`, keep the `{steps_left in 3,4}` localized branch active but replace the UniPC-style slope with the endpoint-Heun slope already used elsewhere in the sampler
portability=direct
base_commit=5e43179
active_nf_range=paper-targeted late full-step regime only; NFE 5/9/11/13 should remain unchanged because the branch is still inactive when `num_steps < 12`
extra_nfe=0
hypothesis=if the paper win is genuinely coming from the UniPC history term, then preserving the same late window and second evaluation but dropping the history reuse should weaken `fid_N35` relative to `5e43179`
expected_signature=`fid_N35 > 6.7513` with unchanged NFE 5/9/11/13; a large collapse is not required, only a clear weakening versus the winning mechanism
ablation=this is the family ablation required by `program.md`; if it does not weaken, the mechanism story is not yet specific enough
kill_condition=any low-NFE drift, any instability in the `{steps_left in 3,4}` window, or no measurable weakening versus `5e43179`


## Candidate Card


family=localized_unipc_preterminal_corrector
kind=simplification
external_anchor=UniPC (Zhao et al., 2023)
borrowed_mechanism=keep the history-aware corrector but test whether only the final standard-regime step before the terminal exact-Heun pair needs it
synthesis_step=from `5e43179`, shrink `RESEARCH_STANDARD_LOCAL_UNIPC_STEPS_LEFT` from `(3, 4)` to `(3,)` while leaving the localized history-aware slope, predictor scale, and terminal exact-Heun pair unchanged
portability=direct
base_commit=5e43179
active_nf_range=paper-targeted late full-step regime only; NFE 5/9/11/13 should remain unchanged because the branch is still inactive when `num_steps < 12`
extra_nfe=0
hypothesis=the history-aware curvature fix may be concentrated on the last standard-regime step before the terminal exact-Heun pair, so a one-step window could preserve most of the `5e43179` gain while making the mechanism easier to explain
expected_signature=`fid_N35` stays clearly better than the endpoint-Heun-only ablation and remains close enough to `5e43179` to justify the simpler story, with unchanged NFE 5/9/11/13
ablation=if the one-step window softens materially, keep the two-step `5e43179` window as the minimal defensible mechanism
kill_condition=any low-NFE drift or any `fid_N35` result that falls back near the endpoint-Heun-only ablation boundary


## Candidate Card


family=localized_dualfast_preunipc_compensation
kind=mechanism
external_anchor=DualFast: Dual-Speedup Framework for Fast Sampling of Diffusion Models (Yu et al., 2025)
borrowed_mechanism=replace the current score used by the solver with a localized mix of the current score and one cached higher-noise score from the previous step
synthesis_step=keep the `5e43179` two-step `{3,4}` history-aware UniPC window and terminal exact-Heun pair unchanged, but add DualFast-style current-score compensation only on the two earlier approach steps `{5,6}`, reusing the existing late predictor-ramp magnitude as the compensation weight instead of introducing a new tuned schedule
portability=direct
base_commit=5e43179
active_nf_range=late full-step regime; NFE 5/9/11/13 should stay unchanged while NFE 35 and the paper path are active
extra_nfe=0
hypothesis=the current paper winner may still enter the pre-terminal UniPC window with approximation error inherited from the late approach steps; a localized previous-score compensation on `{5,6}` should reduce that entry error and improve `fid_N35` and paper block 0 without disturbing the low-NFE frontier
expected_signature=`fid_N35 < 6.7513` with NFE 5/9/11/13 effectively unchanged; if promoted, paper block 0 should improve beyond `1.93345`
ablation=if this family wins, keep the same `{5,6}` window but remove the higher-noise reuse by zeroing the compensation term, or move the window one step earlier, to verify that the gain is from localized DualFast-style compensation rather than from the mere existence of another late branch
kill_condition=any `fid_N35` regression versus `5e43179`, any low-NFE drift outside the current stable band, or any sign that the added compensation interferes with the winning `{3,4}` UniPC plus terminal exact-Heun structure


## Candidate Card


family=localized_dcsolver_buffer_compensation
kind=mechanism
external_anchor=DC-Solver: Improving Predictor-Corrector Diffusion Sampler via Dynamic Compensation (Zhao et al., 2024)
borrowed_mechanism=replace the buffered previous score used by a predictor-corrector step with a more trajectory-aligned compensated estimate instead of trusting the raw cached score
synthesis_step=restore the `5e43179` winner, keep the `{3,4}` localized UniPC window and terminal exact-Heun pair unchanged, and on the two earlier approach steps `{5,6}` replace `prev_d_cur` inside the late predictor extrapolation with a deterministic blend toward `prev_d_prime`, using the existing predictor-extrapolation magnitude as the local compensation weight
portability=direct
base_commit=5e43179
active_nf_range=late full-step regime; NFE 5/9/11/13 should stay unchanged while NFE 35 and the paper path are active
extra_nfe=0
hypothesis=the failed DualFast screen suggests the approach error is not in the current slope itself but in the buffered history being slightly misaligned with the corrected trajectory; a localized compensated buffer on `{5,6}` should improve entry into the winning pre-terminal UniPC window and beat `fid_N35=6.7513` without disturbing the frontier
expected_signature=`fid_N35 < 6.7513` with NFE 5/9/11/13 effectively unchanged; if promoted, paper block 0 should improve beyond `1.93345`
ablation=if this family wins, keep the same `{5,6}` window but remove the compensated blend back to raw `prev_d_cur`, or move the same compensated-buffer rule into the `{3,4}` window, to test whether the gain is really from localized buffer alignment rather than from another late branch
kill_condition=any `fid_N35` regression versus `5e43179`, any low-NFE drift outside the current stable band, or any paper block-0 loss that mirrors the failed DualFast translation miss


## Candidate Card


family=localized_unipc_preterminal_corrector
kind=simplification
external_anchor=UniPC (Zhao et al., 2023)
borrowed_mechanism=keep the history-aware corrector but test whether only the earlier of the two pre-terminal standard-regime steps carries the transferable gain
synthesis_step=from `5e43179`, shrink `RESEARCH_STANDARD_LOCAL_UNIPC_STEPS_LEFT` from `(3, 4)` to `(4,)` while leaving the localized history-aware slope, predictor scale, and terminal exact-Heun pair unchanged
portability=direct
base_commit=5e43179
active_nf_range=paper-targeted late full-step regime only; NFE 5/9/11/13 should remain unchanged because the branch is still inactive when `num_steps < 12`
extra_nfe=0
hypothesis=the proxy-only success of `{3}` but paper loss on block 0 suggests the paper-side gain may be entering through the earlier pre-terminal correction, not the final one; a `{4}`-only window could therefore be a simpler paper-faithful mechanism
expected_signature=`fid_N35` stays below the endpoint-Heun-only ablation and remains near the two-step base closely enough to justify a paper check, with unchanged NFE 5/9/11/13
ablation=if the `{4}`-only window also misses, keep the two-step `5e43179` window as the minimal paper-qualified story
kill_condition=any low-NFE drift or any `fid_N35` result that falls back near the endpoint-Heun-only ablation boundary


## Candidate Card


family=localized_xtheta_multistep_approach
kind=mechanism
external_anchor=DPM-Solver++: Fast Solver for Guided Sampling of Diffusion Probabilistic Models (Lu et al., 2022)
borrowed_mechanism=use multistep history in data-prediction space x_theta instead of relying only on drift-space history
synthesis_step=keep the 5e43179 winner unchanged on the {3,4} localized UniPC window and terminal exact-Heun pair, but on the two earlier approach steps {5,6} replace the current drift-space predictor extrapolation with a localized AB2-style x_theta extrapolation built from the current and previous denoised predictions, then convert it back to drift only for those steps
portability=direct
base_commit=5e43179
active_nf_range=late full-step regime; NFE 5/9/11/13 should remain unchanged while NFE 35 and the paper path are active
extra_nfe=0
hypothesis=data-prediction history may align the approach into the winning pre-terminal UniPC window better than drift-history compensation, so a localized x_theta multistep switch should beat fid_N35=6.7513 without reproducing the paper miss seen from current-slope compensation
expected_signature=`fid_N35 < 6.7513` with the low-step band effectively unchanged; if promoted, paper block 0 should improve beyond `1.93345`
ablation=if this family wins, keep the same {5,6} window but revert to raw drift-space predictor extrapolation, or move the same x_theta multistep rule into the {3,4} window, to test whether the gain truly comes from localized x_theta history reuse
kill_condition=any `fid_N35` regression versus `5e43179`, any low-NFE drift outside the stable band, or any paper block-0 loss that repeats the failed DualFast translation pattern


## Candidate Card


family=localized_era_basis_selection
kind=mechanism
external_anchor=ERA-Solver: Error-Robust Adams Solver for Fast Sampling of Diffusion Probabilistic Models (Li et al., 2023)
borrowed_mechanism=adaptively choose the lower-error history basis for the predictor instead of trusting one fixed Adams-style previous state
synthesis_step=keep the 5e43179 winner unchanged on the {3,4} localized UniPC window and terminal exact-Heun pair, and only on the two earlier approach steps {5,6} choose the predictor history between prev_d_cur and prev_d_prime by whichever is closer to the current drift, then use that selected basis in the existing late extrapolation rule
portability=direct
base_commit=5e43179
active_nf_range=late full-step regime; NFE 5/9/11/13 should remain unchanged while NFE 35 and the paper path are active
extra_nfe=0
hypothesis=the failed compensation variants suggest the issue is not adding another correction term but trusting the wrong late history basis; localized ERA-style basis selection should improve fid_N35 beyond 6.7513 without perturbing the frontier
expected_signature=`fid_N35 < 6.7513` with the low-step band effectively unchanged; if promoted, paper block 0 should improve beyond `1.93345`
ablation=if this family wins, keep the same {5,6} window but force the predictor to always use prev_d_cur or always use prev_d_prime, to verify that the gain comes from basis selection rather than one history being globally better
kill_condition=any `fid_N35` regression versus `5e43179`, any low-NFE drift outside the stable band, or any proxy signature that looks indistinguishable from the failed compensation family


## Candidate Card


family=localized_era_basis_selection
kind=tuning
external_anchor=ERA-Solver: Error-Robust Adams Solver for Fast Sampling of Diffusion Probabilistic Models (Li et al., 2023)
borrowed_mechanism=probe whether one specific lower-error history basis is better than adaptive or fixed-raw history on the late predictor
synthesis_step=from the failed adaptive-basis screen, keep the same {5,6} localized ERA window but force the predictor to always use prev_d_prime there, while leaving the {3,4} UniPC window and terminal exact-Heun pair unchanged
portability=direct
base_commit=5e43179
active_nf_range=late full-step regime; NFE 5/9/11/13 should remain unchanged while NFE 35 and the paper path are active
extra_nfe=0
hypothesis=the adaptive selector may simply be too noisy with only one-step history, while the corrected-history basis prev_d_prime could still be the consistently better late Adams basis and improve fid_N35 beyond 6.7513
expected_signature=`fid_N35 < 6.7513` with the low-step band effectively unchanged; if it loses again, the ERA family should be closed after two misses
ablation=this is the complementary one-sided ablation to the failed adaptive selector; the other endpoint is already represented by the base sampler's default prev_d_cur history
kill_condition=any `fid_N35` regression versus `5e43179`, any low-NFE drift outside the stable band, or a result that lands in the same miss band as the adaptive ERA screen
