import itertools
import json
devices = list('ABCDEFGH')
links = [('A', 'H', 1), ('A', 'E', 2), ('B', 'F', 4), ('C', 'G', 1), ('C', 'D', 1), ('C', 'E', 1), ('D', 'H', 3), ('G', 'H', 1)]
best_sum = None
for order in itertools.permutations(devices):
    positions = {device: idx for idx, device in enumerate(order)}
    total = sum(count * abs(positions[left] - positions[right]) for left, right, count in links)
    if best_sum is None or total < best_sum:
        best_sum = total
if best_sum is None:
    raise RuntimeError('no cabling solution found')
print(json.dumps({'final_sum': best_sum}))