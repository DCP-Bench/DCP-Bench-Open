from pychoco.model import Model

N = 4
GIVENS = {(0, 0): 1, (1, 2): 4}  # (row, column) -> value

model = Model()
cell = [[model.intvar(1, N, name=f"c{i}{j}") for j in range(N)] for i in range(N)]
for i in range(N):
    model.all_different(cell[i]).post()
    model.all_different([cell[k][i] for k in range(N)]).post()
for (i, j), value in GIVENS.items():
    model.arithm(cell[i][j], "=", value).post()

solver = model.get_solver()
solution = solver.find_solution()
if solution is None:
    print("no Latin square")
else:
    print("Latin square found")
    for row in cell:
        print(" ".join(str(solution.get_int_val(v)) for v in row))
