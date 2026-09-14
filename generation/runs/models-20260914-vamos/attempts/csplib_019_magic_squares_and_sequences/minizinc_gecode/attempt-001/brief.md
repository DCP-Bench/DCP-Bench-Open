# csplib_019_magic_squares_and_sequences (magic sequence)

A magic sequence x of length n has x[i] equal to the number of times i occurs in
x, for every i in 0..n-1.

- Instance input: `n`.
- Output: `x` — n integers in 0..n-1.
- Satisfaction. Constraint: x[i] = count of value i in x, for all i.
- The reference's search speedups (sum(x) = n, sum(i*x[i]) = n) are commented
  out; not carried over.
