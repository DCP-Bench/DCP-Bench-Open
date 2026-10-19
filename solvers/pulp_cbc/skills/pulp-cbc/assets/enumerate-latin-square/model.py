"""Enumerate every 3x3 Latin square by adding a no-good cut after each solution."""
import pulp

N = 3
prob = pulp.LpProblem("latin_all", pulp.LpMinimize)  # satisfaction: no objective
x = prob.add_variable_dicts("x", (range(N), range(N), range(1, N + 1)), cat="Binary")

for i in range(N):
    for j in range(N):
        prob += pulp.lpSum(x[i][j][v] for v in range(1, N + 1)) == 1
for i in range(N):
    for v in range(1, N + 1):
        prob += pulp.lpSum(x[i][j][v] for j in range(N)) == 1
        prob += pulp.lpSum(x[j][i][v] for j in range(N)) == 1

# Every binary is a decision, so two solutions differ exactly when some binary
# differs. The no-good cut for a 0/1 solution says: at least one of its
# variables must take the other value.
flat = [x[i][j][v] for i in range(N) for j in range(N) for v in range(1, N + 1)]
solutions = []
while True:
    status = prob.solve(pulp.PULP_CBC_CMD(msg=False))
    if pulp.LpStatus[status] != "Optimal":  # Infeasible: nothing left
        break
    chosen = [round(pulp.value(b)) for b in flat]
    solutions.append(chosen)
    ones = [b for b, c in zip(flat, chosen) if c == 1]
    zeros = [b for b, c in zip(flat, chosen) if c == 0]
    prob += pulp.lpSum(1 - b for b in ones) + pulp.lpSum(zeros) >= 1, f"no_good_{len(solutions)}"

print("Solutions found:", len(solutions))
print("Final status:", pulp.LpStatus[status])
