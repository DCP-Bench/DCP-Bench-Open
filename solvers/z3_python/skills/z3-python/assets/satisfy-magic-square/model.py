"""Magic square of order 3 with Z3: every row, column and diagonal sums to the same value."""
import z3

N = 3
cells = [[z3.Int(f"c{i}_{j}") for j in range(N)] for i in range(N)]
flat = [c for row in cells for c in row]
target = N * (N * N + 1) // 2  # the magic constant, 15 for N = 3

solver = z3.Solver()
solver.add([z3.And(c >= 1, c <= N * N) for c in flat])
solver.add(z3.Distinct(flat))
lines = cells + [list(col) for col in zip(*cells)]
lines += [[cells[i][i] for i in range(N)], [cells[i][N - 1 - i] for i in range(N)]]
solver.add([z3.Sum(line) == target for line in lines])

if solver.check() != z3.sat:
    raise SystemExit(f"status: {solver.check()}")

model = solver.model()
grid = [[model.eval(c, model_completion=True).as_long() for c in row] for row in cells]
for row in grid:
    print(" ".join(f"{v:2d}" for v in row))
print(f"magic constant: {target}")
sums = [sum(line) for line in grid] + [sum(col) for col in zip(*grid)]
sums += [sum(grid[i][i] for i in range(N)), sum(grid[i][N - 1 - i] for i in range(N))]
print(f"all lines sum to {target}: {all(s == target for s in sums)}")
