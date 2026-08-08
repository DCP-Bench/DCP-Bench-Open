
import cpmpy as cp
import json

# We model the 3x3 pattern:
#  positions indices:
#  0 1 2
#  3 4 5
#  6 7 8
#
# Where positions with circles: 0,2,6,8
# Squares: 1,3,5,7
# Center (4) is empty -> set to 0
#
# Each square equals the sum of its two adjacent circles:
# pos1 = pos0 + pos2
# pos3 = pos0 + pos6
# pos5 = pos2 + pos8
# pos7 = pos6 + pos8
#
# Place digits 1..8 in the 8 circle/square positions (center is 0).

# Model definition
model = cp.Model()

# Decision Variables: positions 0..8, center (index 4) will be fixed to 0
positions = cp.intvar(0, 8, shape=9, name="positions")

# Center is empty
model += (positions[4] == 0)

# Other positions must be digits 1..8
for i in range(9):
    if i != 4:
        model += (positions[i] >= 1)
        model += (positions[i] <= 8)

# All non-center values are distinct -> they will form a permutation of 1..8
noncenter = [positions[i] for i in range(9) if i != 4]
model += cp.AllDifferent(noncenter)

# Sum constraints for squares
model += (positions[1] == positions[0] + positions[2])  # top middle
model += (positions[3] == positions[0] + positions[6])  # middle left
model += (positions[5] == positions[2] + positions[8])  # middle right
model += (positions[7] == positions[6] + positions[8])  # bottom middle

# Solve and print
if model.solve():
    solution = {'positions': positions.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
