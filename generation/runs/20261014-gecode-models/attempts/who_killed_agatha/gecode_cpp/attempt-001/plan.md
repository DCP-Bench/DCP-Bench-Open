Someone in Dreadsbury Mansion killed Aunt Agatha. (killer: one-hot over 3 people, killer = 0,1,2)
  -> killer IntVar 0..n-1 with channel(*this, is_killer, killer) [one-hot Booleans, x_i = 1 iff killer = i]
Agatha, the butler, and Charles live in Dreadsbury Mansion, and are the only ones to live there. (n = 3 from instance names; domain of killer)
  -> IntVar killer(*this, 0, n-1)
A killer always hates his victim (the victim is Agatha) -> is_killer[i] -> hates[i][Agatha]: clause(BOT_OR, pos={hates[i][0]}, neg={is_killer[i]}, 1)
and is no richer than his victim -> is_killer[i] -> not richer[i][Agatha]: clause(BOT_OR, pos={}, neg={is_killer[i], richer[i][0]}, 1)
Charles hates noone that Agatha hates -> hates[0][x] -> not hates[2][x] for all x: clause(BOT_OR, pos={}, neg={hates[0][x], hates[2][x]}, 1)
Agatha hates everybody except the butler -> hates[0][x] = 1 for x != butler, hates[0][butler] = 0: rel(BoolVar, IRT_EQ, 1/0). No map row fits a fixed Boolean; unit assignment (only two facts).
The butler hates everyone not richer than Aunt Agatha -> not richer[x][0] -> hates[1][x]: clause(BOT_OR, pos={richer[x][0], hates[1][x]}, neg={}, 1) for all x
The butler hates everyone whom Agatha hates -> hates[0][x] -> hates[1][x]: clause(BOT_OR, pos={hates[1][x]}, neg={hates[0][x]}, 1) for all x
Noone hates everyone -> for each x exists y with not hates[x][y]: clause(BOT_OR, pos={}, neg={hates[x][y] for all y}, 1). No map row for a Boolean matrix row; the clause is the global form for "at least one false".
"richer" is a comparison: taken as a strict order over the people (irreflexive, asymmetric, transitive) so it behaves like a wealth comparison. Clauses over richer[x][y] (not stated in the description, implied by "richer").
Branching: killer first (INT_VAR_NONE), then the one-hot Booleans, then hates and richer Booleans (BOOL_VAR_NONE, BOOL_VAL_MIN). Satisfaction, so no objective. Output killer.
