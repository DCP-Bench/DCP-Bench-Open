# csplib_008_vessel_loading on huub_rust: lessons

Not accepted. Every free check (`evaluation.check`, 2 solutions) on the example (json row 0) fails
with `invalid_solution`, detail "Declared outputs cannot extend to a reference solution".

Checked by hand: the solver's reported solutions are valid tilings of the 5x5 deck under
exclusive ends, inclusive ends, and the width/length swap. The runner's output values match the
model, so the failure is not a harness or encoding bug.

Variants tried (all fail on the example, the same detail):
- attempt-001: container orientation free (90-degree rotation through element), exclusive ends.
- attempt-002: fixed orientation, exclusive ends (right = left + width, bottom = top + length).
- inclusive ends (right = left + width - 1); length along the deck width; both; 1-based coordinates.
- json:3 (tiling_rotation) with rotation: same detail.

Open question for the reference: which convention or extra constraint it enforces that a valid
placement of the example violates. The modelling was blind (brief, JSON, contracts, skill), so
the reference was not read. The example's containers fill the deck exactly, so any touching
placement is a tiling; a reference that forbids touching or uses a strict gap would reject
every placement.

Note: the dataset note on tiling_rotation says a model without rotation fails that instance; with the
given orientations the containers cannot fill the 10x6 deck, so the note is consistent with rotation being allowed.
