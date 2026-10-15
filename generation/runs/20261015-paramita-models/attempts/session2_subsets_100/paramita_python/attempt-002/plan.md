Out of a set of integers, you are given a list of different integers (A, ten values).
  -> instance["A"], read by the model; no value typed in.
find two disjoint non-empty subsets, S and T
  -> one Bool per element for S (in_S[i]) and one for T (in_T[i]); S and T disjoint: ~(in_S[i] & in_T[i]) per i; non-empty: sum(in_S) >= 1 and sum(in_T) >= 1.
such that the sum of elements in S equals the sum of elements in T
  -> sum(A[i] * in_S[i]) == sum(A[i] * in_T[i]) (linear PB over 0/1 Bools; values at most 100, sums at most 1000, well inside 32 bits).
S union T does not need to be all ten elements of A
  -> no constraint: elements may be in neither set.
Print in_S and in_T, lists of the same length as A, 1 for in the subset, 0 otherwise
  -> outputs {"in_S": [Bool per element], "in_T": [Bool per element]}.
Objective: none (satisfaction).
