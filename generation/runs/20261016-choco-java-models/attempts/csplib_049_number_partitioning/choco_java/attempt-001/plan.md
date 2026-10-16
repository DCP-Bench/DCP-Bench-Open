Partition the numbers 1..N into two sets A and B such that:
  "partition of numbers 1..N into two sets A and B" -> a[k], b[k] over 1..n, all of a and b together form a permutation of 1..n: m.allDifferent(a ++ b, "AC")
  "A and B have the same cardinality" -> both arrays have length n/2 (instance field n)
  "sets are increasing" (output order) -> m.increasing(a, 1), m.increasing(b, 1)
  "sum of numbers in A = sum of numbers in B" -> sum(a) = total/2, total = n(n+1)/2 -> m.sum(a, "=", total/2)
  "sum of squares in A = sum of squares in B" -> sum of a_k^2 = totalSquares/2 -> m.square(sq[k], a[k]), m.sum(sq, "=", totalSq/2)
  "print the sets A and B" -> out A = a, out B = b
Objective: none (satisfaction).
