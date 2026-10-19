"""Minimise the cost of staff that together cover every required skill (set cover)."""
import pulp

SKILLS_NEEDED = {"python", "sql", "cloud"}
STAFF = {  # name: (cost, skills)
    "Ana": (4, {"python", "sql"}),
    "Ben": (3, {"sql"}),
    "Cem": (5, {"python", "cloud"}),
    "Dee": (2, {"cloud"}),
    "Eli": (6, {"python", "sql", "cloud"}),
}

prob = pulp.LpProblem("skill_cover", pulp.LpMinimize)
hire = prob.add_variable_dicts("hire", list(STAFF), cat="Binary")

for skill in SKILLS_NEEDED:
    prob += pulp.lpSum(hire[name] for name, (_, skills) in STAFF.items() if skill in skills) >= 1, f"cover_{skill}"

prob += pulp.lpSum(cost * hire[name] for name, (cost, _) in STAFF.items())  # the objective

status = prob.solve(pulp.PULP_CBC_CMD(msg=False))
print("Status:", pulp.LpStatus[status])
if prob.sol_status == pulp.LpSolutionOptimal:
    chosen = [name for name in STAFF if round(hire[name].varValue) == 1]
    print("Chosen:", ", ".join(chosen))
    print("Total cost:", round(pulp.value(prob.objective)))
