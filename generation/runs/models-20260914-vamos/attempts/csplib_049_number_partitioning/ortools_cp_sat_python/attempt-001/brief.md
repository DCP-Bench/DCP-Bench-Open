# csplib_049_number_partitioning

Partition 1..n into two sets of equal cardinality, equal sum and equal sum of
squares.

- Instance input: `n` (even).
- Outputs: `A` and `B`, each a list of n/2 integers in 1..n. The reference builds
  them as variables `x` and `y` but declares them as `A` and `B`.
- Satisfaction. Constraints: AllDifferent(x + y together), sum(x) = sum(y),
  sum(x^2) = sum(y^2).
- The reference's symmetry breaking is commented out; not carried over.
