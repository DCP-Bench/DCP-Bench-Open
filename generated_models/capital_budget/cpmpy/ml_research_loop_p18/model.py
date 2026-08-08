import itertools
import json
npv = [16, 22, 12, 8]
cost = [5, 7, 4, 3]
budget = 14
best = None
for x in itertools.product([0, 1], repeat=4):
    used = sum(item_cost * chosen for item_cost, chosen in zip(cost, x, strict=True))
    value = sum(item_npv * chosen for item_npv, chosen in zip(npv, x, strict=True))
    if used <= budget and (best is None or value > best[0]):
        best = (value, x)
if best is None:
    raise RuntimeError('no capital budget solution found')
print(json.dumps({'x': list(best[1])}))