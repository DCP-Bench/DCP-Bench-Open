"""All optimal solutions: every minimum-cost assignment of 3 workers to 3 tasks.

Step 1 finds the optimum. Step 2 fixes the cost to that optimum and enumerates
the assignments with no-good cuts over the assignment binaries.
"""
from docplex.mp.model import Model

COST = [
    [1, 1, 3],
    [1, 1, 3],
    [3, 3, 3],
]
N = len(COST)

m = Model(name="assignment-all-optimal")
x = m.binary_var_matrix(range(N), range(N), name="x")  # dict keyed by (worker, task)
for i in range(N):
    m.add_constraint(m.sum(x[i, j] for j in range(N)) == 1)  # one task per worker
for j in range(N):
    m.add_constraint(m.sum(x[i, j] for i in range(N)) == 1)  # one worker per task

cost = m.sum(COST[i][j] * x[i, j] for i in range(N) for j in range(N))
m.minimize(cost)
best = m.solve()
if best is None:
    raise SystemExit(f"no assignment: {m.solve_details.status}")
optimum = round(best.objective_value)
print(f"Optimal cost: {optimum} ({m.solve_details.status})")

# keep only optimal solutions: the cost must equal the optimum from now on
m.add_constraint(cost == optimum)
found = []
while True:
    sol = m.solve()
    if sol is None:
        break
    picks = [[round(sol[x[i, j]]) for j in range(N)] for i in range(N)]
    found.append([next(j for j in range(N) if picks[i][j] == 1) for i in range(N)])
    # no-good over the assignment binaries
    m.add_constraint(
        m.sum(1 - x[i, j] for i in range(N) for j in range(N) if picks[i][j] == 1)
        + m.sum(x[i, j] for i in range(N) for j in range(N) if picks[i][j] == 0) >= 1
    )

print(f"Optimal assignments: {len(found)}")
for task_of_worker in found:
    print("  worker -> task " + str(task_of_worker))
