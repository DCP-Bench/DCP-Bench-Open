# Assign four workers to four jobs, one each, at minimum total cost.
from hermax.model import Model

COST = [
    [9, 2, 7, 8],
    [6, 4, 3, 7],
    [5, 8, 1, 8],
    [7, 6, 9, 4],
]
N = len(COST)

m = Model()
x = m.bool_matrix("x", N, N)  # x[i][j]: worker i does job j
for i in range(N):
    m &= x.row(i).exactly_one()
for j in range(N):
    m &= x.col(j).exactly_one()

# Paying cost[i][j] whenever x[i][j] is true makes the broken weight the total cost.
for i in range(N):
    for j in range(N):
        m.obj[COST[i][j]] += ~x[i][j]

r = m.solve()
if r.status != "optimum":
    raise SystemExit(f"status: {r.status}")
assigned = [next(j for j in range(N) if r[x[i][j]]) for i in range(N)]
print("job of each worker:", assigned)
print(f"Total cost: {r.cost}")
