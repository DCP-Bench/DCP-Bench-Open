# csplib_044_steiner

n*(n-1)/6 triples over 1..n, any two sharing at most one element.

- Instance input: `n`. Output: `sets` — an n_sets x n Boolean matrix (0/1),
  sets[i][j] true when element j is in triple i.
- Satisfaction. Every row has exactly three ones; any two rows overlap in at
  most one column. The reference's symmetry breaking is commented out.
