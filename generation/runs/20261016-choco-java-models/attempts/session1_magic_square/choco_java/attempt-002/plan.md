A magic square is an n x n grid (n != 2)
-> square: IntVar[n][n] with domains 1..n^2
each cell contains a different integer from 1 to n^2
-> m.allDifferent(all cells, "AC")
the sum of the integers in each row ... is equal
-> m.sum per row = magic, equal to the common sum
the sum in each column is equal
-> m.sum per column = magic
the sum in each diagonal is equal
-> m.sum on main diagonal and anti-diagonal = magic
the sum ... has to be equal to n(n^2+1)/2 (integer)
-> magic = n(n^2+1)/2 computed from instance n (always an integer for n != 2)
Objective: satisfaction (no objective)
Search change after attempt-001 timed out on n=6 (json:4): dom/wdeg over the cells with Luby restarts (skill Search section), replacing min-domain first-fail without restarts.
