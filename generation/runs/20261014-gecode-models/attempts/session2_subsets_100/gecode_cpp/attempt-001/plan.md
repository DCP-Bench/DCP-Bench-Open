Find two disjoint non-empty subsets S and T of A whose element sums are equal (print membership as in_S, in_T).
- "a list of different integers A" -> instance field A, n = A.size(), not a variable.
- "S and T are disjoint" (no element in both) -> per element i: s[i] + t[i] <= 1 -> linear(*this, BoolVarArgs(s[i],t[i]), IRT_LQ, 1) (no map row for disjoint Booleans; this is the one-line pairwise form).
- "sum of elements in S equals sum of elements in T" -> linear(*this, w, x, IRT_EQ, 0) with x = s ++ t and w = A ++ (-A) [weighted count, map row "how many / weighted count"].
- "S is non-empty" -> linear(*this, s, IRT_GQ, 1).
- "T is non-empty" -> linear(*this, t, IRT_GQ, 1).
- "S union T does not need to be all of A" -> no constraint.
- Branching: branch on in_S then in_T with BOOL_VAR_NONE, BOOL_VAL_MIN (decision variables only).
- Objective: none (satisfaction).
