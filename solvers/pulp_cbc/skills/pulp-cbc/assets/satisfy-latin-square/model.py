"""Fill a 4x4 Latin square that matches the clues: a satisfaction problem (no objective)."""
import pulp

N = 4
CLUES = {(0, 0): 1, (1, 2): 4, (2, 3): 2, (3, 1): 3}  # (row, column) -> value in 1..N

prob = pulp.LpProblem("latin_square", pulp.LpMinimize)  # no objective is added
x = prob.add_variable_dicts("x", (range(N), range(N), range(1, N + 1)), cat="Binary")

for i in range(N):
    for j in range(N):
        prob += pulp.lpSum(x[i][j][v] for v in range(1, N + 1)) == 1  # one value per cell
for i in range(N):
    for v in range(1, N + 1):
        prob += pulp.lpSum(x[i][j][v] for j in range(N)) == 1         # each value once per row
        prob += pulp.lpSum(x[j][i][v] for j in range(N)) == 1         # and once per column
for (i, j), v in CLUES.items():
    prob += x[i][j][v] == 1                                           # clue

status = prob.solve(pulp.PULP_CBC_CMD(msg=False))
print("Status:", pulp.LpStatus[status])
if pulp.LpStatus[status] == "Optimal":
    grid = [[round(pulp.value(pulp.lpSum(v * x[i][j][v] for v in range(1, N + 1)))) for j in range(N)]
            for i in range(N)]
    for row in grid:
        print(" ".join(map(str, row)))
    ok = all(sorted(row) == list(range(1, N + 1)) for row in grid) and all(
        grid[i][j] == v for (i, j), v in CLUES.items())
    print("Valid Latin square matching the clues:", ok)
