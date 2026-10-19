"""Satisfy: complete a 4x4 Sudoku (0 marks a blank cell)."""
from ortools.sat.python import cp_model

GRID = [
    [1, 2, 0, 4],
    [0, 4, 1, 0],
    [0, 1, 4, 0],
    [4, 0, 0, 1],
]
N = len(GRID)
B = 2  # box side

model = cp_model.CpModel()
cell = [[model.new_int_var(1, N, f"c{r}{c}") for c in range(N)] for r in range(N)]

for r in range(N):
    for c in range(N):
        if GRID[r][c]:
            model.add(cell[r][c] == GRID[r][c])

for i in range(N):
    model.add_all_different(cell[i])                      # row i
    model.add_all_different([cell[r][i] for r in range(N)])  # column i
for br in range(0, N, B):
    for bc in range(0, N, B):
        model.add_all_different([cell[br + r][bc + c] for r in range(B) for c in range(B)])

solver = cp_model.CpSolver()
status = solver.solve(model)
print(solver.status_name(status))
if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
    for row in cell:
        print(" ".join(str(solver.value(v)) for v in row))
