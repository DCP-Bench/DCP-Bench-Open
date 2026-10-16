Problem: futoshiki. Fill an n x n grid with digits 1..n so each row and column holds each digit once, given digits stay fixed, and each inequality clue holds.

- each row contains each of the digits 1 to n once -> m.allDifferent(row, "AC") per row (values in 1..n)
- each column contains each of the digits 1 to n once -> m.allDifferent(col, "AC") per column
- some digits are given at the start -> grid[r][c] = given digit (fixed with eq(v).post())
- one square must be lower than its neighbour (lt clue, 1-based r1 c1 r2 c2) -> m.arithm(a, "<", b) per clue
- objective: none, satisfaction; output grid -> out.put("grid", grid)
