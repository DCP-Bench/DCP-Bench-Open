Hidato Puzzles start semi-filled with numbered tiles -> the given tiles in the instance puzzle (non-zero entries) are fixed: x[c][v] is true for each given cell c with value v.
Connect the numbers together to win -> every cell holds exactly one value and every value from 1 to n^2 is in exactly one cell: one-hot Bool x[c][v], sum over v == 1 per cell, sum over c == 1 per value.
Consecutive number must touch horizontally, vertically, or diagonally -> for each value k and cell c: x[c][k] implies Or of x[d][k+1] over the 8-neighbours d of c.
The numbers must be in increasing order -> implied by the consecutive-touching chain from 1 to n^2 over the one-hot values.
Fill in the empty cells with the numbers that complete the puzzle -> outputs x[i][j] = sum(v * x[c][v]) over v.
objective -> none (satisfaction).
