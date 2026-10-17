# 0/1 knapsack: pick items to maximise total value within a weight capacity.
# Data comes from a JSON file given as the first argument (default: data.json next to this file).
# Every size is read from the data, and keys the model does not use are ignored.
import json
import sys
from pathlib import Path

import mip

path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).with_name("data.json")
data = json.loads(path.read_text())
values, weights, capacity = data["values"], data["weights"], data["capacity"]
n = len(values)

m = mip.Model(sense=mip.MAXIMIZE, solver_name="CBC")
m.verbose = 0
m.max_mip_gap = 0.0       # OPTIMAL then means proven, not within 0.01 %
m.max_mip_gap_abs = 0.0

# one binary per item: 1 when the item is packed
take = [m.add_var(f"take_{i}", var_type=mip.BINARY) for i in range(n)]

# the packed items weigh at most the capacity
m += mip.xsum(weights[i] * take[i] for i in range(n)) <= capacity

# the objective is the total value of the packed items
m.objective = mip.xsum(values[i] * take[i] for i in range(n))

status = m.optimize(max_seconds=60)
if status == mip.OptimizationStatus.OPTIMAL:
    packed = [i for i in range(n) if take[i].x > 0.5]
    print("Optimal value:", round(m.objective_value))
    print("Items:", packed)
else:
    print("Status:", status.name)
