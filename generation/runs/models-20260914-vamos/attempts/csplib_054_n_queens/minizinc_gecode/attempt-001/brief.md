# csplib_054_n_queens

Place n queens on an n x n board so none attacks another (row, column, diagonal).

- Instance inputs: `n` (board size / number of queens).
- Output: `queens` — list of n integers in 1..n; `queens[i]` is the column of the
  queen in row i.
- Satisfaction problem, no objective.
- Constraints (from the reference): `AllDifferent(queens)`,
  `AllDifferent(queens - arange(n))`, `AllDifferent(queens + arange(n))`.
