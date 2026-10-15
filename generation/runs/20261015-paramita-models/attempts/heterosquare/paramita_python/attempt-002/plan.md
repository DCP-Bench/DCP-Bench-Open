A heterosquare of order n is a n*n square -> cell (i,j) holds one of the values 1..n^2: one-hot Bool x[i][j][v], exactly one value per cell.
whose elements are distinct integers from 1 to n^2 -> each value v used by exactly one cell: sum over cells of x[i][j][v] == 1.
the sums of the rows, columns and diagonals -> each of the 2n+2 line sums is linked to a unary (order) encoding u[a][k] = [line sum >= lo + k]; the PB link is sum(v * x over the line) == lo + sum(u[a]). Unary is chosen because the line sums are summed and compared, and pairwise PB comparisons of two wide sums blew up memory in attempt-001.
are all different -> for every pair of lines (a, b): some position k where u[a][k] and u[b][k] differ, via one Bool per (a, b, k) implying the difference and an Or over k.
Print a heterosquare (x) of a given order as a list of lists of integers -> outputs x[i][j] = sum(v * x[i][j][v]) over v.
objective -> none (satisfaction).
