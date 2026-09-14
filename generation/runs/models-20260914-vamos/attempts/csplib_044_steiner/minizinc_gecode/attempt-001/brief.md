# csplib_044_steiner

Find n*(n-1)/6 triples over 1..n such that any two triples share at most one
element (a ternary Steiner system).

- Instance input: `n`.
- Output: `sets` — an n_sets x n Boolean matrix, n_sets = n*(n-1)/6, where
  sets[i][j] is true when element j belongs to triple i.
- Satisfaction. Constraints: every row has exactly three true entries; any two
  rows share at most one true column.
- The reference's symmetry breaking (fixing sets[0][0]) is commented out; not
  carried over.
