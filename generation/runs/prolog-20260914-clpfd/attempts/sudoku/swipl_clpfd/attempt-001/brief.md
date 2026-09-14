# sudoku

Fill the grid so every row, column and block holds each value once.

- Instance input: `input_grid`, a square matrix whose zeros are empty cells.
- Output: `grid` — the completed matrix, values 1..n for an n x n grid.
- Satisfaction. The reference is written for 9 x 9 with 3 x 3 blocks; this model
  takes the size from the instance and its block size as the square root, which
  is the same thing for every square grid.
