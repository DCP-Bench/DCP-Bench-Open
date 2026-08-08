
import cpmpy as cp
import json

# Positions:
# Circles: C positions are 1,3,6,8 (as per pattern C F C / F   F / C F C)
# Squares: F positions are 2,4,5,7
# The grid layout with positions:
# pos: 1  2  3
#      4     5
#      6  7  8
#
# Constraints:
# Each square is sum of adjoining circles
# Adjoining means orthogonally adjacent (up, down, left, right)
#
# Adjacencies:
# 2(F): adjacent to circles 1(C) and 3(C)
# 4(F): adjacent to circles 1(C) and 6(C)
# 5(F): adjacent to circles 3(C) and 8(C)
# 7(F): adjacent to circles 6(C) and 8(C)

model = cp.Model()

# Variables
# Positions 1 to 8 are variables with domain 1..8, distinct
positions = cp.intvar(1, 8, shape=8, name="pos")

# All positions must be distinct
model += cp.AllDifferent(positions)

# Naming convenience
# Circles: pos[0]=1, pos[2]=3, pos[5]=6, pos[7]=8
# Squares: pos[1]=2, pos[3]=4, pos[4]=5, pos[6]=7

# Constraints for squares equals sum of adjoining circles
model += (positions[1] == positions[0] + positions[2])  # pos 2 = pos1 + pos3
model += (positions[3] == positions[0] + positions[5])  # pos 4 = pos1 + pos6
model += (positions[4] == positions[2] + positions[7])  # pos 5 = pos3 + pos8
model += (positions[6] == positions[5] + positions[7])  # pos 7 = pos6 + pos8

if model.solve():
    solution = {'positions': [int(v) for v in positions.value().tolist()]}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
