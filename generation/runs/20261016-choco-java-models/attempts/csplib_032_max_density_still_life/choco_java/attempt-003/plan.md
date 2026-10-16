Problem: max-density still life on an n x m active grid (cells outside the grid are dead).
grid[i][j] = 1 if cell (i,j) is live -> BoolVar matrix, output "grid".
A live cell must have exactly 2 or 3 live neighbours -> live => neighbour sum >= 2 and <= 3 (ifThen).
A dead cell must not have exactly 3 live neighbours -> neighbour sum = 3 => live (ifThen).
A dead cell just outside the grid must not have exactly 3 live neighbours -> ring cell neighbour sum != 3.
Neighbour counts: sum(IntVar[], "=", IntVar) over the in-grid 8-neighbourhood.
Symmetry breaking (lex-leader over the grid's symmetries: flips, rotation by 180, and the diagonal ones when n = m) -> lexLessEq(grid, image) per symmetry.
Objective: maximise the number of live cells -> sum of grid cells, MAXIMIZE.
Symmetry breaking and LCG as in attempt 2.
Search: activity-based heuristic over the grid cells, to find dense solutions and learn from failures.
