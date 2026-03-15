# Literature Pass pass_16

pass_id=pass_16
session_date=2026-03-15
working_paper_base=e2379ec
trigger=the first ERK-guided terminal-Heun paper run on `af251d0` preserved the `e2379ec` row shape but still lost on all three paper blocks by tiny margins.
pass_kind=reflection
primary_anchor=none
technical_check_refs=erk_guid_2026, pass_14, pass_15
next_move=calibration_probe
highest_value_rationale=The highest-value next move is a single smaller-scale calibration probe, not a family rotation yet, because the first paper row was an unusually clean near-tie: proxy improved, the paper row stayed within about `+0.00012` mean of the base, and every block moved only slightly in the same direction, which is a classic signature of mild over-correction.
reflection_verdict=existing_literature_sufficient
followup_question=none

## Reflection Takeaway

- `af251d0` finished at `1.92392/1.96425/1.98166`, versus the `e2379ec` base `1.92366/1.96423/1.98159`.
- The family is still alive because the loss is tiny, uniform, and mechanically coherent: the ERK correction did not destabilize the row or scramble the seed-block shape.
- The single most informative next probe is to reduce `w_stiff` from `0.75` to `0.5` while leaving the localization and `w_con=0.5` gate unchanged.
- If the smaller scale still loses on paper, close the ERK-guided family and rotate; do not spend more tuning budget on threshold scans or wider placements.
