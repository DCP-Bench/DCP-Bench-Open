
import cpmpy as cp
import json

# Data
# Guests: 0=Andrew, 1=Betty, 2=Cara, 3=Dave, 4=Erica, 5=Frank
# Allowed neighboring pairs (undirected): {0-3, 0-5, 1-2, 1-4, 2-5, 3-4}
allowed_undirected = [(0,3),(0,5),(1,2),(1,4),(2,5),(3,4)]
# Create ordered pairs for both directions
allowed_pairs = []
for a,b in allowed_undirected:
    allowed_pairs.append((a,b))
    allowed_pairs.append((b,a))
# End of data

# Model definition
model = cp.Model()

# Decision Variables
x = cp.intvar(0, 5, shape=6, name="x")  # seating order around the circular table
model += cp.AllDifferent(x)

# Symmetry breaking (fix Andrew at seat 0 and fix direction)
model += (x[0] == 0)
model += (x[1] < x[5])

# Constraints and conflict minimization
# allowed_b[i] = 1 if pair (x[i], x[i+1]) is allowed, else 0
allowed_b = cp.boolvar(shape=6, name="allowed_b")

for i in range(6):
    j = (i + 1) % 6
    # allowed if (x[i], x[j]) matches any allowed pair
    allowed_exprs = [ (x[i] == a) & (x[j] == b) for (a,b) in allowed_pairs ]
    model += (allowed_b[i] == cp.any(allowed_exprs))

# Minimize number of conflicts = 6 - sum(allowed_b)
conflicts = cp.sum([1 - allowed_b[i] for i in range(6)])
model.minimize(conflicts)

# Solve and print
if model.solve():
    solution = {'x': x.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
