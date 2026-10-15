The futoshiki puzzle is played on a square grid -> grid of n x n cells, n = len(values); one-hot Bool v[r][c][k] for digit k in 1..n in cell (r,c), exactly one digit per cell
place the numbers 1 to 5 (or whatever the dimensions are) -> integer g[r][c] = sum k*v[r][c][k]
each row contains each of the digits 1 to n -> for each row r and digit k: sum over c of v[r][c][k] == 1
each column contains each of the digits 1 to n -> for each column c and digit k: sum over r of v[r][c][k] == 1
Some digits may be given at the start -> for each given values[r][c] = k > 0: v[r][c][k] is true
inequality constraints between some squares, one must be higher or lower than its neighbour -> lt entry [r1,c1,r2,c2] (1-based): g[r1][c1] + 1 <= g[r2][c2]
Print the completed grid (grid) as a list of lists of integers -> output grid[r][c] = g[r][c]
Objective: none (satisfaction)
