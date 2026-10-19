"""Minimise: fewest coins that add up to an amount. Reads the JSON instance named on the command line (default: data.json next to this file)."""
import json
import sys
from pathlib import Path

from ortools.sat.python import cp_model

path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent / "data.json"
with open(path) as f:
    data = json.load(f)  # extra keys in the file are ignored
coins, amount = data["coins"], data["amount"]

model = cp_model.CpModel()
# uses[i] = how many coins of denomination coins[i]; each count is bounded by the amount
uses = [model.new_int_var(0, amount // c, f"uses{c}") for c in coins]
model.add(sum(c * u for c, u in zip(coins, uses)) == amount)
model.minimize(sum(uses))

solver = cp_model.CpSolver()
status = solver.solve(model)
print(solver.status_name(status))
print(f"Minimum coins: {int(solver.objective_value)}")
for coin, count in zip(coins, uses):
    print(f"  {coin} x {solver.value(count)}")
