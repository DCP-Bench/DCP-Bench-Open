# Plan: calvin_puzzle attempt-001

Grid: n by n squares, completely filled -> one-hot Bools p[r][c][k] (square (r,c) holds number k+1), k in 0..n^2-1
completely fill every square -> per square: sum over k of p[r][c][k] == 1
each number is placed once -> per number: sum over squares of p[r][c][k] == 1
Movement Type I (vertically or horizontally, exactly three squares away) -> offsets (0,+-3), (+-3,0)
Movement Type II (diagonally, exactly two squares away) -> offsets (+-2,+-2)
the next number is placed by one of the two movement types from the previous one -> per square and k: ~p[r][c][k] | Or(p[square at a move offset][k+1]), inside the grid
print the completed grid x -> integer expression sum((k+1) * p[r][c][k]) per square
objective -> none (satisfaction)
