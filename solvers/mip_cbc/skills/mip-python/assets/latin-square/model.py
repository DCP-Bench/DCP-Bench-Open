# Latin square of order 4 with two given cells: fill a 4 x 4 grid with the values 1..4 so that every
# row and every column contains each value exactly once, keeping the given cells.
# Encoding: a one-hot binary per cell and value. Each cell takes one value, and each value appears
# once per row and once per column (all-different written with binaries).
import mip

n = 4
given = {(0, 0): 1, (2, 3): 4}  # (row, column) -> value, 0-based rows and columns, values 1..n

m = mip.Model(solver_name="CBC")
m.verbose = 0
x = [[[m.add_var(f"x_{r}_{c}_{v}", var_type=mip.BINARY) for v in range(1, n + 1)]
      for c in range(n)] for r in range(n)]

# each cell holds exactly one value
for r in range(n):
    for c in range(n):
        m += mip.xsum(x[r][c]) == 1

# each row holds each value exactly once
for r in range(n):
    for v in range(n):
        m += mip.xsum(x[r][c][v] for c in range(n)) == 1

# each column holds each value exactly once
for c in range(n):
    for v in range(n):
        m += mip.xsum(x[r][c][v] for r in range(n)) == 1

# the given cells keep their values
for (r, c), value in given.items():
    m += x[r][c][value - 1] == 1

# no objective: any feasible grid answers the question
status = m.optimize(max_seconds=60)
if status != mip.OptimizationStatus.OPTIMAL:
    raise SystemExit(f"Status: {status.name}")

grid = [[next(v + 1 for v in range(n) if x[r][c][v].x > 0.5) for c in range(n)] for r in range(n)]
for row in grid:
    print(" ".join(str(v) for v in row))

# check the answer independently of the model
rows_ok = all(sorted(row) == list(range(1, n + 1)) for row in grid)
cols_ok = all(sorted(grid[r][c] for r in range(n)) == list(range(1, n + 1)) for c in range(n))
print("valid:", rows_ok and cols_ok and all(grid[r][c] == v for (r, c), v in given.items()))
