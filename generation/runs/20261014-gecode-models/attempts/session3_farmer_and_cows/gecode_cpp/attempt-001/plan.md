Problem: cows numbered 1..num_cows, cow i gives i litres; cows go to num_sons sons, son s gets cows_per_son[s] cows; every son gets the same total milk.

Requirement: every cow goes to exactly one son -> channel(*this, bools_of_cow_i, cow_i, 0) (one-hot Boolean row per cow, cow_i is the son)
Requirement: son s receives cows_per_son[s] cows -> count(*this, cow, s, IRT_EQ, cows_per_son[s]) (per-son count, domain consistent)
Requirement: each son's milk total is the same (total milk / num_sons, total = n(n+1)/2) -> linear(*this, IntArgs(1..n), bools_of_son_s, IRT_EQ, share, IPL_DOM) per son
Requirement: sons with equal cow counts are interchangeable -> precede(*this, cow, IntArgs(group)) per group of >= 2 sons with equal counts; no group, no constraint (valid only where sons are interchangeable)
Branching -> branch(*this, son_cows, BOOL_VAR_NONE(), BOOL_VAL_MAX()) one son at a time, larger cows first (the cow-level branching of the first draft timed out on the 81-cow instance)
Objective -> none (satisfaction)
