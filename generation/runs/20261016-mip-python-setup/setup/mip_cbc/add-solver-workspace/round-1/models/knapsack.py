import json
import sys

import mip

data = json.load(open(sys.argv[1]))
values, weights, capacity = data["values"], data["weights"], data["capacity"]
n = len(values)

m = mip.Model(sense=mip.MAXIMIZE, solver_name="CBC")
m.verbose = 0
m.max_mip_gap = 0.0
m.max_mip_gap_abs = 0.0
# one binary per item: 1 when the item is packed
take = [m.add_var(f"take_{i}", var_type=mip.BINARY) for i in range(n)]

# the packed items weigh at most the capacity
m += mip.xsum(weights[i] * take[i] for i in range(n)) <= capacity

# the objective is the total value of the packed items
m.objective = mip.xsum(values[i] * take[i] for i in range(n))

status = m.optimize(max_seconds=60)
if status == mip.OptimizationStatus.OPTIMAL:
    print(json.dumps({"take": [round(t.x) for t in take]}))
else:
    raise SystemExit(f"Status: {status.name}")
