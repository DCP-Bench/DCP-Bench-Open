Problem: knight's tour on an n x n board: a sequence of knight moves visiting every square exactly once (open tour, no return to start). x[i][j] = move number, 0..n*n-1.

- "visits every square exactly once" -> x cells in 0..n*n-1, allDifferent (AC) over the flattened board
- "tour is represented by integers from 0 to n*n-1" -> domains 0..n*n-1; cellOf[p] = square visited at move p, inverseChanneling(flat, cellOf)
- "sequence of moves of a knight" -> consecutive moves p, p+1: cellOf[p] and cellOf[p+1] are a knight's move apart -> table (Tuples true) of allowed knight-move pairs
- "without returning to the starting square" -> no circuit constraint; the path is open
- objective: none (satisfaction)
- output x as IntVar[n][n]
