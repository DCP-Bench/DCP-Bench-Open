An order m quasigroup is a Latin square of size m: an m x m table in which each element from 1 to m occurs exactly once in every row and every column -> puzzle[i][j] in 1..N, allDifferent per row and per column (AC)
complete a partially filled quasigroup; the given cells (start, 0 = empty) keep their values -> arithm(puzzle[i][j], "=", start[i][j]) for each non-zero cell
Print the completed quasigroup (puzzle) -> out.put("puzzle", puzzle)
Objective: none (satisfaction)
