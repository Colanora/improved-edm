# Literature Pass pass_18

pass_id=pass_18
session_date=2026-03-15
working_paper_base=e2379ec
trigger=pass_17 concluded that the reviewed pool was exhausted again after closing the ERK-guided family, so another narrow follow-up was required before any new serious edit.
pass_kind=followup_check
primary_anchor=belm_2024
technical_check_refs=pass_06, pndm_2022, unipc_2023, rx_dpm_2025
new_paper_refs=belm_2024
paper_refs=belm_2024
candidate_families=localized_obelm_virtual_predictor
reflection_verdict=existing_literature_sufficient
followup_question=What still-unused deterministic zero-extra-NFE local mechanism remains in recent diffusion-ODE literature after ruling out late history-vector tweaks, embedded error guidance, and offline/search-based solver families?

## Consulted Papers

- [`belm_2024`](../papers/belm_2024.md)

## Session Takeaway

- The narrow follow-up did not uncover a brand-new global solver family, but it did surface one still-viable local residue: the 2-step O-BELM recurrence from the exact-inversion literature.
- O-BELM is still training-free, deterministic, and zero-extra-NFE, yet it is mechanistically different enough from the rejected drift-trend lines to merit one tightly localized probe.
- The right repo-sized transfer is not the paper's whole exact-inversion agenda. It is a single localized state-placement update that uses the previous state and current drift to place the existing late predictor more accurately before the second model evaluation.

## Candidate Card


family=localized_obelm_virtual_predictor
kind=mechanism
external_anchor=BELM: Bidirectional Explicit Linear Multi-step Sampler for Exact Inversion in Diffusion Models (Wang et al., 2024)
borrowed_mechanism=replace a one-step predictor-state extrapolation with the 2-step O-BELM state recurrence, using the current state, the immediately previous state, and the current derivative without extra model evaluations
synthesis_step=from the exact `e2379ec` paper base, keep the `{4}` midpoint entry step, `{3}` UniPC corrector, and the two terminal exact-Heun stages unchanged, but replace the lone `{steps_left=5}` virtual-predictor state placement with a full-step O-BELM predictor state evaluated at `t_next`, then reuse the existing second evaluation and corrector logic
portability=direct
base_commit=e2379ec
active_nf_range=late full-step regime only; the adaptation should matter most around the current paper path and should stay dormant outside the single late predictor slot
extra_nfe=0
hypothesis=the best remaining late-step gap may be a predictor-state placement error rather than an error-direction problem, and O-BELM's LTE-optimized two-state recurrence can correct that more cleanly than the already-closed drift-trend and springboard heuristics
expected_signature=if the recurrence is helpful, the 5k proxy should improve primarily at the high-NFE end without disturbing the rest of the band, and any paper lift should arrive as a small but coherent late-tail gain rather than a noisy one-block spike
ablation=if the family shows life, compare it directly against the current STORK-style predictor on the same `{steps_left=5}` slot rather than adding new placements or coefficient scans
kill_condition=any clear proxy loss, any instability, or a paper row that trails the simpler `e2379ec` base without producing a cleaner full-row story
