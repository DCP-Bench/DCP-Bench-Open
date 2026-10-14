Teams 0..8 = Clem, Duke, FSU, GT, UMD, UNC, NCSt, UVA, Wake. Dates 0..17 (date k = index k-1). Weekends = odd indices (9), weekdays = even indices.
opp[d][i] = opponent of i on d; bye = opp[d][i]==i. where[d][i] in {0 home, 1 bye, 2 away}.
Two-team match symmetry (a plays b iff b plays a) -> channel(opp[d], opp[d]) per date.
Bye iff opp is self; where==1 <-> opp==self -> reified rel per cell.
Home/away complement: where[d][i] + where[d][opp[d][i]] == 2 -> element + linear.
Each team hosts each other team once (play twice, once at home, once away) -> bool (opp==j && where==0) summed over dates == 1, for all ordered pairs.
Each team has 2 byes -> count(opp column i, value i) == 2 (redundant, cheap).
1. Mirroring scheme (r1,r2) 1-based -> opp[r1][i] == opp[r2][i] for all i and pairs.
2. No two final aways -> (where[16][i]==2) >> (where[17][i]!=2).
3. Home/away/bye runs -> sequence on where: away<=2 in 3 (IntSet{2},q3,0..2); home<=2 in 3 ({0},3,0..2); away-or-bye<=3 in 4 ({1,2},4,0..3); home-or-bye<=4 in 5 ({0,1},5,0..4).
4. Weekend pattern -> count over weekend dates of where == 0 is 4, == 2 is 4, == 1 is 1.
5. First weekends -> count of where in {0,1} over the first five weekends (indices 1,3,5,7,9) >= 2.
6. Rival matches on last date (index 17): for every non-FSU team with rival r: opp == r or opp == FSU or opp == self.
7. Constrained matches in dates 11..18 (indices 10..17): count of opp == b in that window >= 1 for (Wake,UNC), (Wake,Duke), (GT,UNC), (GT,Duke).
8. Opponent sequence: forbidding (where,opp) pairs for team i on dates d,d+1: (away,UNC),(away,Duke) and reverse -> extensional forbidden 4-tuples on (where[d][i],opp[d][i],where[d+1][i],opp[d+1][i]).
   No three consecutive dates against UNC, Duke, Wake in any order -> extensional forbidden 3-tuples on (opp[d][i],opp[d+1][i],opp[d+2][i]) with values in {1,5,8} pairwise distinct.
9. Fixed facts: opp[10][UNC]=Duke, opp[17][UNC]=Duke, opp[1][UNC]=Clem, where[15][Duke]=bye, where[16][Wake]!=home, where[0][Wake]=bye, where[17][{Clem,Duke,UMD,Wake}]!=away, where[0][{Clem,FSU,GT,Wake}]!=away, where[17][{FSU,NCSt}]!=bye, where[0][UNC]!=bye.
Branching: where first (INT_VAR_SIZE_MIN, INT_VAL_MIN), then opp (INT_VAR_SIZE_MIN, INT_VAL_MIN). Satisfaction problem.
