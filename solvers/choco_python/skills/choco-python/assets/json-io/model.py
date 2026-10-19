import json
import sys

from pychoco.model import Model

# Usage: python3 model.py instance.json
# Reads one instance file, prints one JSON object on stdout.
with open(sys.argv[1]) as f:
    data = json.load(f)
weights, values, capacity = data["weights"], data["values"], data["capacity"]

model = Model()
take = [model.boolvar(name=f"take{i}") for i in range(len(weights))]
model.scalar(take, weights, "<=", capacity).post()
profit = model.intvar(0, sum(values), name="profit")
model.scalar(take, values, "=", profit).post()

solution = model.get_solver().find_optimal_solution(profit, True)
if solution is None:
    print(json.dumps({"status": "unsatisfiable"}))
else:
    chosen = [solution.get_int_val(t) for t in take]
    print(json.dumps({"status": "optimal", "take": chosen,
                      "profit": solution.get_int_val(profit)}))
