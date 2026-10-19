"""Rota with more shift slots than nurses can fill: an infeasible model, and how to see it."""
import pulp

NURSES = ["Ana", "Ben", "Cem", "Dee"]
SHIFTS = ["early", "late", "night"]
NEEDED_PER_SHIFT = 2
MAX_SHIFTS_PER_NURSE = 1  # 3 shifts x 2 nurses = 6 slots, but only 4 nurses x 1 shift = 4 possible

prob = pulp.LpProblem("rota", pulp.LpMinimize)  # no objective: feasibility only
work = prob.add_variable_dicts("work", (NURSES, SHIFTS), cat="Binary")

for s in SHIFTS:
    prob += pulp.lpSum(work[n][s] for n in NURSES) == NEEDED_PER_SHIFT, f"staff_{s}"
for n in NURSES:
    prob += pulp.lpSum(work[n][s] for s in SHIFTS) <= MAX_SHIFTS_PER_NURSE, f"limit_{n}"

status = prob.solve(pulp.PULP_CBC_CMD(msg=False))
print("Status:", pulp.LpStatus[status])
if pulp.LpStatus[status] == "Infeasible":
    print("No rota exists: do not read variable values after an infeasible status.")
