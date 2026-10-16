# Plan: social golfers (csplib_010)

Golfers: n_groups * group_size. Weeks: n_weeks. Group numbers 0..n_groups-1.
Variable: x[i][j] in 0..n_groups-1 = group of golfer i in week j.

- "golfers play in groups of a specific number" -> count(*this, week_j, k, IRT_EQ, group_size) for every week j and group k (map row: exactly k equal to v)
- "each golfer plays once a week" -> x[i][j] domain 0..n_groups-1 (one group per golfer per week, by variable domain)
- "no golfer plays in the same group as any other golfer on more than one occasion" -> for each pair (a,b): eqs_j = expr(*this, x[a][j] == x[b][j]) over weeks, linear(*this, eqs, IRT_LQ, 1). No map row counts weeks in which a pair meets; decomposition with reified equalities is used because no global fits.
- "group numbers are interchangeable" -> precede(*this, week_j, IntArgs(0..n_groups-1)) per week (map row: interchangeable values)
- branching -> branch over all x, INT_VAR_SIZE_MIN, INT_VAL_MIN
- objective -> none (satisfaction); outputs assign as one list per golfer (Matrix row)
