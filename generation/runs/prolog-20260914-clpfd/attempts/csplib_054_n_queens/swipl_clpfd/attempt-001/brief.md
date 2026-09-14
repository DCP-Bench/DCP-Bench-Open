# csplib_054_n_queens

Place n queens on an n x n board so none attacks another.

- Instance input: `n`.
- Output: `queens` — n integers in 1..n, the column of the queen in each row.
- Satisfaction. Constraints: the columns are all different, and so are the two
  diagonal offsets `queens[i] - i` and `queens[i] + i`.
