from cpmpy import *
import json

# Decision variables
half_crowns = intvar(0, 15, name="half_crowns")
shillings = intvar(0, 15, name="shillings")
sixpences = intvar(0, 15, name="sixpences")

# Model
model = Model()

# Total number of coins is 15
model += [half_crowns + shillings + sixpences == 15]

# Total value in pence is 1 * 240 + 5 * 12 + 6 = 306 pence
# Half-crown = 30 pence, shilling = 12 pence, sixpence = 6 pence
model += [30 * half_crowns + 12 * shillings + 6 * sixpences == 306]

# Solve the model
model.solve()

# Print the solution
solution = {"half_crowns": half_crowns.value()}
print(json.dumps(solution))