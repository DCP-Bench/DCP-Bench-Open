Problem: land every aircraft on one runway at an exact time within its window, in a fixed landing sequence, minimising total penalty.

Time windows: each landing_times[i] within [earliest_landing[i], latest_landing[i]] -> IntVar domain at declaration (per-variable bounds, built from IntVarArgs).
Target time penalty: landing before target costs penalty_before per unit, after costs penalty_after per unit -> per plane pen_i >= penalty_before_i * (target_i - t_i) and pen_i >= penalty_after_i * (t_i - target_i), pen_i >= 0 -> linear (rel) bounds; exact at the optimum because pen_i has positive weight in the minimised sum (no MAX global row fits a two-sided piecewise cost without a helper).
Penalty total: total_penalty = sum pen_i -> expr(sum) (sum row of the map, linear).
Separation between the i-th and j-th aircraft in the fixed sequence (i < j): landing_times[j] - landing_times[i] >= separation_time[i][j] -> rel linear difference, bounds propagation (IPL_BND default; no map row for offset differences, so linear).
Branching: landing_times by INT_VAR_SIZE_MIN, values INT_VAL_MIN (earliest first); then the penalty auxiliaries pen_i by INT_VAR_NONE, INT_VAL_MIN, so none is left open (the driver branches only on outputs and the objective).
Objective: minimize total_penalty.
