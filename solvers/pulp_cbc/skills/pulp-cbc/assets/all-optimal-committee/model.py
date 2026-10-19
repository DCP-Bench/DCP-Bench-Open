"""List every optimal committee: pick 3 of 6 candidates with the highest total score."""
import pulp

SCORES = [5, 5, 3, 3, 3, 1]
K = 3
n = len(SCORES)

prob = pulp.LpProblem("committee", pulp.LpMaximize)
pick = prob.add_variable_dicts("pick", range(n), cat="Binary")
prob += pulp.lpSum(pick[i] for i in range(n)) == K
score = pulp.lpSum(SCORES[i] * pick[i] for i in range(n))
prob += score                                    # the objective

status = prob.solve(pulp.PULP_CBC_CMD(msg=False))
if prob.sol_status != pulp.LpSolutionOptimal:    # proven optimal, not just found
    raise SystemExit(f"No proven optimum: {pulp.LpStatus[status]}")
best = round(pulp.value(score))
print("Optimal score:", best)

# Pin the objective to its optimum, then enumerate with no-good cuts.
prob += score == best, "optimum"
committees = []
while True:
    status = prob.solve(pulp.PULP_CBC_CMD(msg=False))
    if pulp.LpStatus[status] != "Optimal":
        break
    chosen = [i for i in range(n) if round(pulp.value(pick[i])) == 1]
    committees.append(chosen)
    prob += pulp.lpSum(1 - pick[i] for i in chosen) + pulp.lpSum(pick[i] for i in range(n) if i not in chosen) >= 1, f"no_good_{len(committees)}"

print("Optimal committees:", len(committees))
for c in committees:
    print("  candidates", c)
