# Plan: csplib_026 sports tournament scheduling

Encoding: one-hot for teams in home[w][p] (H) and away[w][p] (A); M[w][p][i][j] auxiliary for "i and j play in (w,p)".

- "a tournament of n teams over n-1 weeks, with each week divided into n/2 periods" -> weeks w < n-1, periods p < n/2; one game per (w,p).
- "The first team in each slot plays at home, whilst the second plays the first team away" -> exactly one H and one A true per (w,p) -> sum_t H == 1, sum_t A == 1.
- "every team plays once a week" -> per (w,t): sum_p (H+A) == 1.
- "every team plays at most twice in the same period over the tournament" -> per (p,t): sum_w (H+A) <= 2.
- "every team plays every other team" -> per pair i<j: sum_{w,p} M == 1, with M <-> (H_i & A_j | H_j & A_i).
- Output home[w][p], away[w][p] as 1-based team numbers: sum((t+1) * H) and sum((t+1) * A).
- Objective: none (satisfaction).
