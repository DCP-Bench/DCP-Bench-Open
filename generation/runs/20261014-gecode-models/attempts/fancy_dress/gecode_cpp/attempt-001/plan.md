Problem: Mr Greenguest's dress party; choose 0/1 for tie t, hat h, shirt r, socks s; fee n is 1 when the dress rules fail; minimise cost.
Rules 1-3 are soft: each becomes a Boolean rule_k = expr(...) (MiniModel, no hard rel). The rule Booleans are needed because a broken rule costs the fee, not a fail.
Rule 1: a green tie requires a green shirt -> rule1 = expr((t == 0) || (r == 1))
Rule 2: green socks and green shirt only if green tie or green hat -> rule2 = expr((s == 0) || (r == 0) || (t == 1) || (h == 1))
Rule 3: green shirt or green hat or no green socks requires green tie -> rule3 = expr((r == 0 && h == 0 && s == 1) || (t == 1))
Rule 4: not dressed by rules 1-3 pays 11 -> dressed = expr(rule1 && rule2 && rule3); rel(*this, n != dressed)
Costs: tie 10, hat 2, socks 12, fee 11, shirt 9 unless green (owned green shirt, so 9 - 9r) -> cost = expr(linear), minimize(cost)
Branching: BOOL_VAR_NONE over t, h, r, s (decisions), then n (auxiliary, fixed by propagation).
