
import cpmpy as cp
import json

ratings = [2, 3, 4, 4, 4, 2, 1, 3, 4]

n = len(ratings)
candies = cp.intvar(1, n, shape=n)

model = cp.Model()

for i in range(n - 1):
    current = ratings[i]
    next_r = ratings[i + 1]
    if current > next_r:
        model += (candies[i] > candies[i + 1])
    elif current < next_r:
        model += (candies[i] < candies[i + 1])

model.minimize(cp.sum(candies))

if model.solve():
    solution = {'z': int(model.objective_value())}
    print(json.dumps(solution))
else:
    print("No solution found.")
