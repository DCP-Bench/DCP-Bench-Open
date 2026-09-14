# csplib_049_number_partitioning

Split 1..n into two halves of equal size, equal sum and equal sum of squares.

- Instance input: `n` (even). Outputs: `A` and `B`, each n/2 integers in 1..n
  (the reference builds them as `x` and `y` but declares them as `A` and `B`).
- Satisfaction. all_different over both halves together, equal sums, equal sums
  of squares. The symmetry breaking in the reference is commented out.
- The half-totals below are implied, not extra: the all_different constraint
  already forces the two halves to partition 1..n, so each carries half of
  sum(1..n) and half of sum of squares. They are written multiplied out so no
  division has to be exact.
