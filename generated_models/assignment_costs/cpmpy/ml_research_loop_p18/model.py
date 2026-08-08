import itertools
import json
cost = [[14, 5, 8, 7, 15], [2, 12, 6, 5, 3], [7, 8, 3, 9, 7], [2, 4, 6, 10, 1]]
best = None
for people in itertools.permutations(range(5), 4):
    total = sum(cost[task][people[task]] for task in range(4))
    if best is None or total < best[0]:
        best = (total, people)
if best is None:
    raise RuntimeError('no assignment solution found')
x = [[1 if best[1][task] == person else 0 for person in range(5)] for task in range(4)]
print(json.dumps({'x': x}))