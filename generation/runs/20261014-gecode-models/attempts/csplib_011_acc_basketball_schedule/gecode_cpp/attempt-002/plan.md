Teams 0..8 = Clem, Duke, FSU, GT, UMD, UNC, NCSt, UVA, Wake. Dates 0..17 (index = statement date - 1). Weekends = odd indices, weekdays = even indices.
opp[d][i] = opponent of i on d, i itself on a bye. where[d][i] in {0 home, 1 bye, 2 away}.
Mirroring (1-based pairs (1,8),(2,9),(3,12),(4,13),(5,14),(6,15),(7,16),(10,17),(11,18)) -> second date of a pair shares the opp variables (aliasing), and where of the pair sums to 2 -> rel sum == 2.
Bye iff opp is self -> reified rel (where==1) == (opp==i).
Match symmetry (i plays j iff j plays i) -> channel(opp[d], opp[d]) per date.
Opposite sides of a match (one home, one away) -> element(where[d], opp[d][i], other), where[d][i] + other == 2.
Each ordered pair plays once at home -> sum over dates of bool(opp==j && where==0) == 1 (linear).
Each team: 2 byes (count of own index == 2) and each opponent exactly twice (count == 2).
No two final aways (last two dates) -> (where[16]==2) >> (where[17] != 2).
Home/away/bye runs -> sequence on each team's where column: away<=2 in 3, home<=2 in 3, away-or-bye<=3 in 4, home-or-bye<=4 in 5.
Weekend pattern -> over odd indices: 4 home, 4 away, 1 bye. Weekdays (even indices): same counts (redundant).
First weekends -> count of where in {0,1} over indices 1,3,5,7,9 >= 2.
Rival matches on last date (index 17): non-FSU team i: opp == rival or opp == FSU or opp == i.
Constrained matches in dates 11..18 (indices 10..17): count(opp == b) >= 1 for (Wake,UNC),(Wake,Duke),(GT,UNC),(GT,Duke).
Opponent sequences: extensional forbidden 4-tuples (where,opp,where,opp) on consecutive dates for away UNC/Duke both ways; extensional forbidden 3-tuples of opp on consecutive dates for all permutations of {UNC,Duke,Wake}.
Fixed facts (index form): opp[10][UNC]=Duke, opp[17][UNC]=Duke, opp[1][UNC]=Clem, where[15][Duke]=bye, where[16][Wake]!=home, where[0][Wake]=bye, where[17][{Clem,Duke,UMD,Wake}]!=away, where[0][{Clem,FSU,GT,Wake}]!=away, where[17][{FSU,NCSt}]!=bye, where[0][UNC]!=bye.
Search: where first (AFC, min value), then the opponents of the first date of each mirror pair (AFC, min value); restarts(100). Satisfaction.
Reason for the change from attempt 1: attempt 1 found one solution but not a second in 180 s; deciding where first with restarts found two solutions in about 11 s on a quick check.
