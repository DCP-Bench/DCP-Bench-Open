import itertools
import json

demands = [4, 8, 10, 7, 12, 4]
best = None
for x in itertools.product(range(max(demands) + 1), repeat=len(demands)):
    if all(x[i] + x[(i - 1) % len(x)] >= demands[i] for i in range(len(x))):
        total = sum(x)
        if best is None or total < best[0]:
            best = (total, list(x))
print(json.dumps({"x": best[1]}))
