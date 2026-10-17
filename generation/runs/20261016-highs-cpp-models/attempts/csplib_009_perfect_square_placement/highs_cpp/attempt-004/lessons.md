# csplib_009_perfect_square_placement, highs_cpp: lessons

Accepted on 4 of 6 available instances (example, json:1, json:3, json:4). Not retained:
4/6 = 0.67 is below the 0.8 bar.

- json:5 (base 30, 19 squares) times out at 180 s with every formulation tried.
- json:6 (base 112, 21 squares) times out in attempt-001/002 and runs out of memory (2048 MB)
  with the exact-cover model in attempt-004.

What was tried:
- attempt-001: pairwise non-overlap with four binaries per pair, big-M = base. Timeout on json:5, json:6.
- attempt-002: adds unit-line cover rows (each line k crossed by squares summing to base). Same timeouts.
- attempt-003: attempt-002 with tighter per-line big-Ms and symmetry breaking on the largest square
  (reflection and transposition). Free check: json:5 still times out. Not evaluated.
- attempt-004: exact cover. Binary per (square, position), one position per square, each unit cell
  covered exactly once, integer x and y tied to the chosen position, ordering among equal squares.
  Accepted on 4 of 6. json:5 times out at 180 s. json:6 is killed at the 2048 MB limit.

Next steps, if this problem is taken up again: a stronger bound for json:5 is needed (for example
a different search space or cuts from the largest squares' fixed corners). Exact cover is too big
for base 112 in memory, so json:6 needs a different encoding or is a performance limit.
