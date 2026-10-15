# Plan: knights_tour (attempt-002)

Change from attempt-001: attempt-001 timed out on the 10x10 instance (execution_timeout). Same one-hot step encoding, plus a redundant backward link so the solver propagates from both ends of each move.

- "a sequence of moves of a knight on a chessboard" -> v[k][s] one-hot: knight on square s at move k (k in 0..n*n-1)
- "visits every square exactly once" -> per square: sum over k of v[k][s] == 1
- "one square per move" -> per move k: sum over s of v[k][s] == 1
- "each move is a knight move" (forward) -> per k, s: If(v[k][s], Or(v[k+1][t] for t knight-neighbour of s))
- "each move is a knight move" (backward, redundant) -> per k, t: If(v[k+1][t], Or(v[k][s] for s knight-neighbour of t))
- "move number" output x[i][j] -> sum over k of k * v[k][(i,j)]
- "without returning to the starting square" -> no closing move
- satisfaction problem, no objective
