Out of a set of integers, you are given a list of different integers -> A[j] for j in 0..n-1 with n = len(A), constants from the instance
find two disjoint non-empty subsets S and T -> per element j: Bool in_S[j], Bool in_T[j]; disjoint: `~(in_S[j] & in_T[j])`
S and T are non-empty -> `sum(in_S) >= 1`, `sum(in_T) >= 1` (PB over the Bools)
the sum of elements in S equals the sum of elements in T -> `sum(A[j] * in_S[j]) == sum(A[j] * in_T[j])` (one PB constraint, weights A[j] at most 100)
S union T does not need to be all of A -> no constraint on elements in neither set
Print which elements are in S (in_S) and in T (in_T) as lists of 0/1 -> outputs in_S, in_T as lists of Bools
objective -> none (satisfaction)
