abs(*this, expr(*this, x[i+1] - x[i]), d[i], IPL_DOM) links a difference to an interval variable without a MiniModel relation.
distinct on the diffs with domain 1..n-1 forces them to be a permutation; no extra constraint needed.
restarts(100) with INT_VAR_AFC_SIZE_MAX on x solved n=20 in under 8 s.
