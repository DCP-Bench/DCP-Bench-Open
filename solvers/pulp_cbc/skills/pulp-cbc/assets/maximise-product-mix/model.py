"""Product mix: maximise profit from integer production under resource limits, data from data.json."""
import json
from pathlib import Path

import pulp

data = json.loads(Path(__file__).with_name("data.json").read_text(encoding="utf-8"))
products = data["products"]
resources = data["resources"]

prob = pulp.LpProblem("product_mix", pulp.LpMaximize)
units = {p: prob.add_variable(f"units_{k}", lowBound=0, upBound=data["max_units"][k], cat="Integer")
         for k, p in enumerate(products)}

for name, res in resources.items():
    use = res["use"]
    prob += pulp.lpSum(use[k] * units[p] for k, p in enumerate(products)) <= res["capacity"], name

prob += pulp.lpSum(data["profit"][k] * units[p] for k, p in enumerate(products))  # the objective

status = prob.solve(pulp.PULP_CBC_CMD(msg=False))
print("Status:", pulp.LpStatus[status])
if prob.sol_status == pulp.LpSolutionOptimal:
    for p in products:
        print(f"{p}: {round(units[p].varValue)}")
    print("Profit:", round(pulp.value(prob.objective)))
