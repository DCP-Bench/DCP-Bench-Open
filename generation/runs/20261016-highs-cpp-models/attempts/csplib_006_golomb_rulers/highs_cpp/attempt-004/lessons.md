# csplib_006_golomb_rulers, highs_cpp: lessons

Evaluated: accepted at the top level, but 3 of 5 instances checked (0.6 < 0.8), so not retained.
Solved and proven: sizes 5, 7 and 8 (optima 11, 25, 34; about 0.1 s, 4 s and 35-40 s).
Timed out at 180 s, no proven optimum: size 9 (optimum 44) and size 10 (optimum 55).

What failed or did not help:
- attempt-001 (ordering form, big-M, L = 2^m - 1): times out on size 10 at once.
- attempt-002 (same ordering form, L from the Erdos-Turan Sidon set, tighter variable
  bounds, length >= m(m-1)/2, reflection symmetry break, a DFS-found ruler as L): still
  times out on size 9 and 10. The LP bound is weak (about m(m-1)/2) and each pair
  disjunction is a big-M row, so the tree is large. Not evaluated.
- attempt-004 (position form: binary per position, one y per (t, d) with at most one pair
  per difference, window cuts n <= (1 + sqrt(1 + 8w))/2, and mark positions tied to the
  binaries through an assignment): solves 5, 7 and 8 but not 9 or 10.

Smaller L helps the size-8 solve time a little (DFS bound). The window cuts did not move
size 9 under 180 s.

Not tried: a stronger lower bound on the length (the proof gap is about 10 for size 9 and 10),
or a different search (for example a CP-style model). These would need a new skill or contract
discussion rather than another MIP variant.
