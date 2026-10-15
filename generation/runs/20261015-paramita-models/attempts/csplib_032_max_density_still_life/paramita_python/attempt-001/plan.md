# Plan: csplib_032 max density still life

- n x m active grid of cells, each a Bool (live = 1) -> c[i][j]
- neighbour count N(i,j) = sum of live cells among the 8 neighbours inside the grid -> PB integer expression
- a live cell has 2 or 3 live neighbours -> If(c, 2 <= N <= 3)
- a dead cell has not exactly 3 live neighbours -> Or(c, N <= 2, N >= 4)
- a dead cell just outside the grid has not exactly 3 live neighbours -> same rule for ring positions i in -1..n, j in -1..m outside the grid (neighbours only inside the grid)
- objective: maximise the number of live cells -> sum of all c (linear, unit weights)
- output grid -> n lists of m Bools
