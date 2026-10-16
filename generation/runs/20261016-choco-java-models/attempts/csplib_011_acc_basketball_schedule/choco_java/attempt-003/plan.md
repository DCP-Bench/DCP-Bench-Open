Teams in description order: 0 Clem, 1 Duke, 2 FSU, 3 GT, 4 UMD, 5 UNC, 6 NCSt, 7 UVA, 8 Wake; date d is index d-1
Mirror pairs (0-based dates) p: opp[p][i] shared by both dates; one opponent variable per team per pair (9 pairs)
Each team plays each other once home once away -> per team, allDifferent over its 9 pair opponents (self = bye) -> "AC"
Opponent is symmetric in a pair (x_i=j <=> x_j=i, fixed point = bye) -> inverseChanneling(opp[p], opp[p])
Date: where[d][i] in {0 home, 1 bye, 2 away}; bye <=> opponent is self -> table on (opponent, where)
Partner side: where[d][i] + where[d][opp] = 2 -> element + arithm (bye: 1+1)
Home/away flips across a mirror pair -> where[a][i] + where[b][i] = 2
Per date: 4 home, 4 away, 1 bye -> count (redundant)
1. Mirroring: pairs (1,8),(2,9),(3,12),(4,13),(5,14),(6,15),(7,16),(10,17),(11,18) -> shared opponent arrays
2. No two final aways: forbid (away, away) on dates 17, 18
3. No more than two away in a row, two home in a row -> forbidden 3-windows; three away-or-bye in a row, four home-or-bye in a row -> forbidden 4- and 5-windows
4. Weekends (even dates 2..18): each team 4 home, 4 away, 1 bye on those 9 dates -> count
5. First five weekends (dates 2,4,6,8,10): home or bye on at least two -> boolean isLeq(where,1), sum >= 2
6. Last date (18): a team other than FSU plays FSU, itself (bye) or its rival -> unary table; rivals Duke-UNC, Clem-GT, NCSt-Wake, UMD-UVA
7. Wake-UNC, Wake-Duke, GT-UNC, GT-Duke occur at least once in dates 11..18 -> sum of isEq over dates 11..18 >= 1
8. No team away against UNC and Duke on consecutive dates (forbidden 4-tuples); no three consecutive dates against UNC, Duke, Wake in any order (6 permutations forbidden)
9. Other constraints: UNC v Duke dates 11 and 18 (one pair); UNC v Clem date 2; Duke bye date 16; Wake not home date 17; Wake bye date 1; Clem/Duke/UMD/Wake not away date 18; Clem/FSU/GT/Wake not away date 1; FSU and NCSt no bye date 18; UNC no bye date 1
Output config[d][i] = opponent (self on bye); where[d][i] as above
Objective: none (satisfaction)
Search: domOverWDeg on the 81 pair opponents, then on the 162 where variables; Luby restarts
