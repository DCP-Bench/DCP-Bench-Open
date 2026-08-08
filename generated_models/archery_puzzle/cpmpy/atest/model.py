from cpmpy import *
import json

# Decision variables
# Number of hits on each target
hits = intvar(0, 100, shape=6, name="hits")

# Target scores
targets = [16, 17, 23, 24, 39, 40]

# Model
model = Model()

# Total score is as close to 100 as possible
total_score = sum(hits * targets)
model.minimize(abs(total_score - 100))

# Solve the model
model.solve()

# Print the solution
solution = {"hits": hits.value().tolist()}
print(json.dumps(solution))