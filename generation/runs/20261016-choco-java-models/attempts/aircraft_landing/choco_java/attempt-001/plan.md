Aircraft landing on one runway, fixed landing sequence: aircraft i lands at t_i, in order i = 0..n-1 -> t_i in [earliest_i, latest_i] (m.intVar with bounds).
Minimum separation between the landings of any two aircraft -> for all i<j: t_j - t_i >= separation[i][j] (arithm(t_j, "-", t_i, ">=", sep)).
Penalty for landing earlier than the target -> early_i >= target_i - t_i (arithm(early_i, "+", t_i, ">=", target_i)), penalty_before per minute early.
Penalty for landing later than the target -> late_i >= t_i - target_i (arithm(late_i, "-", t_i, ">=", -target_i)), penalty_after per minute late.
Total penalty -> total = sum penalty_before_i * early_i + penalty_after_i * late_i (scalar).
Objective: minimize total_penalty. Output landing_times and total_penalty.
