import json
best = None
for large_set in range(201):
    for small_set in range(201):
        if 2 * large_set + 3 * small_set > 160:
            continue
        if 3 * large_set + small_set > 200:
            continue
        profit = 20 * large_set + 5 * small_set
        if best is None or profit > best[0]:
            best = (profit, large_set, small_set)
if best is None:
    raise RuntimeError('no chess set solution found')
print(json.dumps({'max_profit': best[0], 'large_set': best[1], 'small_set': best[2]}))