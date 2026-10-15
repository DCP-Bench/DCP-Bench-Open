# Plan: csplib_011_acc_basketball_schedule (attempt-001)

Variables: home[d,i,j] = team i hosts team j on date d; bye[d,i]; dates 1..18, teams 0..8 (order of the description).

- Each team plays once at home and once away against each other team -> home[d,i,j] summed over dates == 1 -> sum over d of home == 1 per ordered pair.
- A team plays at most one game a date, otherwise it has a bye -> H + A + bye == 1 per (d,i).
- Mirroring pairs (r1,r2): same opponent (or bye) on both dates -> Iff(meet[r1,i,j], meet[r2,i,j]).
- No two final aways: away on 17 and away on 18 not both -> A17 + A18 <= 1.
- No more than 2 away in a row -> sum over 3 consecutive A <= 2.
- No more than 2 home in a row -> sum over 3 consecutive H <= 2.
- No more than 3 away or byes in a row -> sum over 4 consecutive (A + bye) <= 3.
- No more than 4 home or byes in a row -> sum over 5 consecutive (H + bye) <= 4.
- Weekend pattern: 4 home, 4 away, 1 bye over even dates -> PB equalities on the weekend sums.
- First weekends: home or bye on at least two of dates 2,4,6,8,10 -> sum (H + bye) >= 2.
- Rival matches on date 18: each team except FSU meets its rival, or meets FSU, or has a bye -> Or(...) per team.
- Constrained matches: Wake-UNC, Wake-Duke, GT-UNC, GT-Duke each meet at least once on dates 11..18 -> Or over dates.
- Opponent sequences: no two consecutive away games at UNC and Duke (either order) -> ~(home & home) per date pair.
- Opponent sequences: no three consecutive dates vs UNC, Duke, Wake (any order) -> ~(M & M & M) per window and permutation.
- Other constraints: fixed meetings, byes and away/home restrictions from the description, each as a constraint.
- Objective: none (satisfaction). Outputs: config (opponent index, -1 for bye) and where (0 home, 1 bye, 2 away).
