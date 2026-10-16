Schedule n teams over n-1 weeks; each week has n/2 periods with 2 slots (home, away). Slot s of week w is sl[w][s]; home[w][p] = sl[w][2p], away[w][p] = sl[w][2p+1].
every team plays once a week -> distinct(*this, sl[w], IPL_DOM) (n slots, values 0..n-1, each team once)
slot of a team in a week, both ways (team -> slot, slot -> team) -> channel(*this, sl[w], ps[w], IPL_DOM) (0-based)
partner slot of a team (slot xor 1) -> element(*this, IntArgs(s xor 1), ps[w][t], pslot) (constant table, domain consistent)
opponent of a team in a week -> element(*this, sl[w], pslot, opp[w][t]) (variable array indexed by variable)
every team plays every other team (each opponent once over the n-1 weeks) -> distinct(*this, opp[.][t], IPL_DOM) for each team t (n-1 values, distinct, all other teams; no self-play since partner slot differs)
every team plays at most twice in the same period -> count(*this, slots of period p over all weeks, t, IRT_LQ, 2) for each period p and team t (the 2(n-1) entries of period p)
branching: sl with INT_VAR_SIZE_MIN, INT_VAL_MIN (decision variables first); ps and opp are fixed by channel and element.
objective: none (satisfaction).
