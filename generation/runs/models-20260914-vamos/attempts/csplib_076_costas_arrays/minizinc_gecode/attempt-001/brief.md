# csplib_076_costas_arrays

A Costas array of order n is a permutation of 1..n whose difference triangle has
no repeated value in any row.

- Instance input: `n`.
- Output: `costas` — n integers in 1..n (the difference matrix is auxiliary in
  the reference and is not a declared output).
- Satisfaction. Constraints: AllDifferent(costas); for each row i in 0..n-3,
  AllDifferent([costas[j] - costas[j - i - 1] for j in i+1..n-1]).
- The reference's extra search constraints are commented out; not carried over.
