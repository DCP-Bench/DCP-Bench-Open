Schedule a tournament of n teams over n-1 weeks, each week n/2 periods, each period two slots (home, away). Teams numbered 1..n.
  "n teams over n-1 weeks, n/2 periods per week" -> home[w][p], away[w][p] in 1..n (n = instance field n_teams)
  "every team plays once a week" -> per week, allDifferent over the n slots: m.allDifferent(week, "AC")
  "every team plays once a week" (position form) -> slotOf[w][t] with m.inverseChanneling(slot[w], slotOf[w], 1, 0)
  "every team plays at most twice in the same period over the tournament" -> per team t and period p, m.count(t, column, c) with c in 0..2
  "every team plays every other team" -> opp[t][w] = team in the partner slot (element on slot[w]), m.allDifferent(opp[t], "AC")
  symmetry breaking (week 1 fixed to 1v2, 3v4, ...), not in the description: relabelling the teams keeps every solution valid
Objective: none (satisfaction).
Search: default. A custom minDom + Luby strategy on the slots timed out on 8 teams.
