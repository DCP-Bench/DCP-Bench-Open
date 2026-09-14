# csplib_076_costas_arrays

A permutation of 1..n whose difference triangle has no repeated value in a row.

- Instance input: `n`. Output: `costas` — n integers in 1..n (the difference
  matrix is auxiliary in the reference).
- Satisfaction. Row l of the triangle holds costas[j] - costas[j-l] for
  l in 1..n-2. The reference's extra speedup constraints are commented out.
