# Plan: n queens on an n x n board (csplib_054)

- "place n queens so that no two are on the same row" -> queens q_i (row i) take a column 1..n; rows are the index, so no row clash by construction
- "no two queens in the same column" -> m.allDifferent(q, "AC")
- "no two queens on the same diagonal" -> m.allDifferent(q_i + i) and m.allDifferent(q_i - i), via offset views
- "print the column of the queen in each row (queens)" -> output q
- objective: satisfaction (none)
