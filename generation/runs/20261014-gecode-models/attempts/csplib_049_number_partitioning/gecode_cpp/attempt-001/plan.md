Partition the numbers 1..N into two sets A and B.
  Each number 1..N goes to exactly one set; the 2 sets together hold each number once -> x[0..N-1] over 1..N, all different (permutation) -> distinct(*this, x, IPL_DOM)
  Sets A and B have the same cardinality -> A = x[0..k-1], B = x[k..N-1] with k = N/2 (array sizes, no extra constraint)
  Elements of each set are listed in increasing order (sorted output, removes ordering symmetry within a set) -> rel(*this, A[j] < A[j+1]), rel(*this, B[j] < B[j+1])
  Symmetry between A and B (swap) -> 1 is in A -> rel(*this, x[0] == 1)
  Sum of numbers in A = sum of numbers in B -> linear(*this, IntArgs(+1 for A, -1 for B), x, IRT_EQ, 0)
  Sum of squares in A = sum of squares in B -> sq[j] = expr(*this, sqr(x[j])) (one per element, IPL_DEF), then linear(*this, IntArgs(+1 for A, -1 for B), sq, IRT_EQ, 0)
  Branching -> branch on x with INT_VAR_SIZE_MIN, INT_VAL_MIN (satisfaction, no objective)
  Outputs -> A and B as IntVarArray of size k, the first k and last N-k of x.
