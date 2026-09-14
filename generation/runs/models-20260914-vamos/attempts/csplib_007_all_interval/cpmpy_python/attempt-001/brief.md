# csplib_007_all_interval

Find a permutation x of Z_n whose vector of neighbouring absolute differences is
a permutation of 1..n-1.

- Instance input: `n`.
- Outputs: `x` (n integers in 0..n-1), `diffs` (n-1 integers in 1..n-1).
- Satisfaction. Constraints: AllDifferent(x), AllDifferent(diffs),
  diffs[i] = |x[i+1] - x[i]|.
- The reference's symmetry breaking is commented out and is NOT part of the
  contract, so it is not carried over.
