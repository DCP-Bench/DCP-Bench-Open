# Lessons, csplib_008_vessel_loading, attempt 001

Rejected: `invalid_solution`, "Declared outputs cannot extend to a reference solution" on `example`.
The model used right = left + extent, bottom = top + extent (y grows downward), rotation free.

Free checks (no attempt spent), all on the `example` instance (5x5 deck, three containers 5x1, 2x4, 3x4, exact tiling):

- exclusive right/bottom, rotation free, fixed 0, fixed 1: rejected
- inclusive right/bottom (right = left + extent - 1), rotation free, fixed 0, fixed 1: rejected
- bottom = top - extent (top is the high edge), exclusive, rotation free: passes `example`

So the reference reads top as the high y edge. The exclusive-right convention is not decided by this; only the top/bottom direction was tested with the exclusive x convention.

Performance: the flipped-y model with `ic` disjunctions finds no solution for json:1 (16x16, 10 containers) in 100 s with `first_fail` labelling of lefts, tops and rotations. Adding redundant `cumulative/4` from `ic_edge_finder` (x-starts with y-extents against the deck length, and the reverse) did not finish in 100 s either. Next: a different search order (for example largest containers first, or bottom-left `smallest` on tops), or relative-position Booleans per pair.

Reproduce: the scratch variants are in /tmp/eclipseq-scratch/vessel/ (not part of the run).
