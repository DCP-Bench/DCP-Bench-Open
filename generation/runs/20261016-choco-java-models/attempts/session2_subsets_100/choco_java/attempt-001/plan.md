Out of a set of integers, you are given a list of different integers. -> instance field A (IntVar values read via inst.getIntArray("A"))
From this set A you can always find two disjoint non-empty subsets S and T -> in_S[i], in_T[i] BoolVars per element; not both, via m.sum({S_i, T_i}, "<=", 1)
disjoint -> m.sum(new BoolVar[]{S[i], T[i]}, "<=", 1) per element i
sum of elements in S equals sum of elements in T -> m.scalar(in_S ++ in_T, A ++ -A, "=", 0)
non-empty subsets S and T -> m.sum(in_S, ">=", 1), m.sum(in_T, ">=", 1)
S union T does not need to be all ten elements -> no constraint on the union
Print in_S and in_T (1 = in subset) -> out.put("in_S", ...), out.put("in_T", ...)
Objective: none (satisfaction)
