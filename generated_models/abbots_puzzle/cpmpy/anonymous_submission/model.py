# Import libraries
from cpmpy import *
import json

# Decision Variables
men = intvar(0, 100, name="men")  # Number of men
women = intvar(0, 100, name="women")  # Number of women
children = intvar(0, 100, name="children")  # Number of children

# Model
model = Model()

# Constraints
# Total number of people is 100
model += (men + women + children == 100)

# Total bushels distributed is 100 (multiplied by 2 to avoid decimals)
model += (6 * men + 4 * women + children == 200)

# Five times as many women as men
model += (women == 5 * men)

# Solve
model.solve()

# Print solution
solution = {
    "men": men.value(),
    "women": women.value(),
    "children": children.value()
}
print(json.dumps(solution))
# End of CPMPy script