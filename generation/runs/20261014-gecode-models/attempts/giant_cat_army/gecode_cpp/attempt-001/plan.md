# Plan: giant_cat_army (attempt-001)

- the list starts with [0] and has 24 entries, the last one is 14 -> x[0] == 0, x[23] == 14 (rel IRT_EQ)
- every entry is an integer from 0 to 60 -> IntVarArray x(*this, 24, 0, 60)
- all elements are distinct -> distinct(*this, x, IPL_DOM)
- each step adds 5, adds 7, or takes a square root (integer only) -> extensional(*this, x.slice(i,1,2), TupleSet of (a,a+5), (a,a+7), (s*s,s)), finalize; domain consistent table, the table is the transition relation (no map row fits a relation between two successive entries with a disjunction of three shapes)
- 2 is in the list, and every 10 comes after a 2 -> seen2[i] == (seen2[i-1] or x[i]==2) (prefix Booleans); (x[i]==10) >> seen2[i-1]; count(x, 2, IRT_GQ, 1) via seen2[23]; count(x, 10, IRT_EQ, 1)
- 14 comes after 10 -> 14 is the last entry and 10 is distinct from 14, so 10 is before it
- branching: x with INT_VAR_SIZE_MIN, INT_VAL_MIN; then seen2 with BOOL_VAR_NONE
- objective: none (satisfaction); output x
