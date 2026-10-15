"""Satisfy: a 3 x 3 magic square with the numbers 1..9, every line summing to 15."""
from docplex.mp.model import Model

N = 3
TOTAL = N * N
LINE = N * (TOTAL + 1) // 2  # 15

m = Model(name="magic-square")
cell = [[m.integer_var(1, TOTAL, name=f"c{i}{j}") for j in range(N)] for i in range(N)]
flat = [cell[i][j] for i in range(N) for j in range(N)]

# all different: one "!=" per pair of cells
for a in range(TOTAL):
    for b in range(a + 1, TOTAL):
        m.add_constraint(flat[a] != flat[b])

# rows, columns and both diagonals sum to LINE
for i in range(N):
    m.add_constraint(m.sum(cell[i]) == LINE)
    m.add_constraint(m.sum(cell[j][i] for j in range(N)) == LINE)
m.add_constraint(m.sum(cell[i][i] for i in range(N)) == LINE)
m.add_constraint(m.sum(cell[i][N - 1 - i] for i in range(N)) == LINE)

# no objective: a satisfaction problem
sol = m.solve()
if sol is None:
    raise SystemExit(f"no magic square: {m.solve_details.status}")

print(f"Found a magic square with line sum {LINE} ({m.solve_details.status}):")
for i in range(N):
    print("  " + " ".join(f"{sol[cell[i][j]]:.0f}" for j in range(N)))
