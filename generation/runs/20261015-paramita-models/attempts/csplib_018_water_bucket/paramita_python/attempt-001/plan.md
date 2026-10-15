Plan: csplib_018_water_bucket (minimum number of pours to reach goal_state from initial_state)

- Water in 3 buckets with capacities capacities[i]; each bucket amount per step t is one-hot over 0..cap_i, plus PADDING_VALUE after the goal -> one-hot per bucket per step (domain includes padding value) -> one-hot encoding (xv[t][i][v]), exactly one per bucket per step.
- initial state -> xv[0][i][initial_i] fixed.
- goal reached at step t -> at_goal[t] <-> AND_i xv[t][i][goal_i]; done[t] <-> done[t-1] OR at_goal[t]; done[S-1] must hold -> Bool auxiliaries.
- after the goal is reached, the state is padding -> xv[t][i][PADDING] <-> done[t-1] for t >= 1.
- each transfer step t >= 1 that is live (not done[t-1]) is exactly one pour i->j -> tr[t][i][j] Bools, sum(tr[t]) + done[t-1] == 1.
- a pour i->j with source amount p and target amount q moves m = min(p, cap_j - q): new source p - m, new target q + m; the third bucket is unchanged -> If(And(tr, xv_prev[i][p], xv_prev[j][q]), And(xv[t][i][p-m], xv[t][j][q+m])) plus Iff of the third bucket's values.
- objective: minimise number of pours = sum of all tr Bools (= number of live steps).
- output sequence[t][i] = sum of v * xv[t][i][v] over the domain (padding value included as a linear term); output cost = objective expression.
