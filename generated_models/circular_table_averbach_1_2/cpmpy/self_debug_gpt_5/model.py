
import cpmpy as cp
import json

# Model definition
model = cp.Model()

# Decision Variables
# Seats are indexed as 0,1,2 in clockwise order; right neighbor is (i+1)%3
x = cp.intvar(0, 2, name="x")  # seat of X
y = cp.intvar(0, 2, name="y")  # seat of Y
z = cp.intvar(0, 2, name="z")  # seat of Z

american = cp.intvar(0, 2, name="american")  # seat of American
english = cp.intvar(0, 2, name="english")    # seat of English
french = cp.intvar(0, 2, name="french")      # seat of French

# Helper variables for right neighbors
rx = cp.intvar(0, 2, name="rx")  # seat of the recipient of X's pass

# Constraints
# All persons occupy different seats
model += cp.AllDifferent([x, y, z])

# All nationalities occupy different seats
model += cp.AllDifferent([american, english, french])

# Right neighbor mapping
succ = [1, 2, 0]  # right neighbor: i -> succ[i]

# Y passed three hearts to the American: Y's right neighbor is the American
model += (cp.Element(succ, y) == american)

# X passed to the person who passed to the Frenchwoman:
# rx is X's right neighbor (recipient of X's pass)
model += (rx == cp.Element(succ, x))
# That person passed to the Frenchwoman, i.e., their right neighbor is the Frenchwoman
model += (cp.Element(succ, rx) == french)

# Solve and print
if model.solve():
    solution = {
        'x': int(x.value()),
        'y': int(y.value()),
        'z': int(z.value()),
        'american': int(american.value()),
        'english': int(english.value()),
        'french': int(french.value())
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
