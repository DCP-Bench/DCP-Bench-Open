import itertools
import json

amount = 199
types = [1, 2, 5, 10, 25, 50]
available = [20, 10, 15, 8, 4, 2]
best = None
best_count = None
for counts in itertools.product(*(range(limit + 1) for limit in available)):
    if sum(count * value for count, value in zip(counts, types)) == amount:
        total_count = sum(counts)
        if best_count is None or total_count < best_count:
            best_count = total_count
            best = list(counts)
print(json.dumps({"coin_counts": best}))
