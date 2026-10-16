Problem: fill an n x n grid with the numbers 1..n^2, each once. Consecutive numbers k and k+1 are either in the same row or column three squares apart (a two-square gap), or diagonally two squares apart (a one-square gap). Output the grid x.

- "fill every square, each number once" -> sequence s[k] = cell of number k+1 (domain 0..n^2-1), m.allDifferent(s, "AC"); inverse q[cell] = k with m.inverseChanneling(s, q); x[cell] = q[cell] + 1
- "Movement Type I: vertically or horizontally, exactly three squares away" -> legal pair (cell a, cell b) with |dr|=3, dc=0 or dr=0, |dc|=3 -> table over (s[k], s[k+1]) built from the grid size
- "Movement Type II: diagonally, exactly two squares away" -> legal pair with |dr|=|dc|=2 -> same table
- satisfaction, no objective; default search, first trying the sequence in order
