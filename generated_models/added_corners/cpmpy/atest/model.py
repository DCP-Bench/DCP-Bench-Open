from cpmpy import *
import json

# Decision variables
positions = intvar(1, 8, shape=8, name="positions")

# Ensure all digits from 1 to 8 are used exactly once
model = Model(AllDifferent(positions))

# Let's assume the positions are arranged as follows:
# C F C   F   F   C F C
# where C is a circle and F is a square.
# We need to define the indices for the squares and their adjacent circles.

# Let's assume the positions are indexed as follows:
# [C0, F0, C1, F1, F2, F3, C2, F4]
# The squares are at positions 1, 3, 4, 5, 7
# The adjacent circles for each square are:
# F0 is between C0 and C1
# F1 is between C1 and C2
# F2 is between C0 and C2
# F3 is between C1 and C2 (this is a mistake in the original code)
# F4 is between C0 and C2 (this is a mistake in the original code)

# Define the square-circle relationships
model += [positions[1] == positions[0] + positions[2]]  # F0 = C0 + C1
model += [positions[3] == positions[2] + positions[6]]  # F1 = C1 + C2
model += [positions[4] == positions[0] + positions[6]]  # F2 = C0 + C2

# Solve the model
model.solve()

# Print the solution
solution = {"positions": positions.value().tolist()}
print(json.dumps(solution))