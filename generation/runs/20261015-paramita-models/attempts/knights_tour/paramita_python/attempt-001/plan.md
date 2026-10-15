# Plan: knights_tour (attempt-001)

- "a knight's tour is a sequence of moves of a knight on a chessboard" -> one-hot step variables v[k][s] = the knight is on square s at move k (k in 0..n*n-1, s in the n*n squares)
- "the knight visits every square exactly once" -> per square: `sum_k v[k][s] == 1`; per move k: `sum_s v[k][s] == 1`
- "a sequence of moves of a knight" (each move is a knight move) -> per move k and square s: `If(v[k][s], Or(v[k+1][t] for t a knight-neighbour of s))`
- "the move number" output x[i][j] -> `sum_k k * v[k][(i,j)]`, one-hot value so each square's move number is an integer expression
- "without returning to the starting square" -> no closing move constraint
- satisfaction problem: no objective
