# Import libraries
from cpmpy import *
import json
import math

# Decision Variables
M = intvar(0, 9999, shape=(9,9), name="M")  # 9x9 grid for crossfigure

# Helper functions
def is_square(x):
    root = int(math.sqrt(9999))
    return sum([(x == i*i) for i in range(1, root+1)]) >= 1

def is_prime(x):
    constraints = []
    constraints.append(x > 1)
    max_div = int(math.sqrt(9999)) + 1
    for d in range(2, max_div):
        constraints.append((x % d != 0) | (x <= d))
    return constraints

# Model
model = Model()

# Define which cells are fixed (X means blocked/not used)
fixed_positions = [
    (1,4), (2,3), (2,7), (3,2), (3,5), (3,8), (4,1), (4,3), (4,4), (4,5), (4,6), (4,7), (4,9),
    (5,2), (5,5), (6,2), (6,5), (6,8), (7,3), (7,7), (8,5), (9,1), (9,2), (9,3), (9,4), (9,5), (9,6), (9,7), (9,8), (9,9)
]

# Constraint: Fixed positions must be 0 (blocked)
for (i,j) in fixed_positions:
    model += M[i-1][j-1] == 0

# Across clues
model += M[0][0] == 2 * M[7][0]  # 1: 27 across times two
model += M[0][3] == M[3][3] + 71  # 4: 4 down plus seventy-one
model += M[0][6] == M[7][1] + 4  # 7: 18 down plus four
model += M[0][7] == M[5][5] // 16  # 8: 6 down divided by sixteen
model += M[0][8] == M[1][1] - 18  # 9: 2 down minus eighteen
model += M[1][2] == 6 * 144 // 12  # 10: Dozen in six gross
model += M[1][5] == M[4][4] - 70  # 11: 5 down minus seventy
model += M[2][0] == M[7][5] * M[5][2]  # 13: 26 down times 23 across
model += M[2][5] == M[5][5] - 350  # 15: 6 down minus 350
model += M[4][0] == M[6][0] * M[5][2]  # 17: 25 across times 23 across
model += is_square(M[5][3])  # 20: A square number
model += is_prime(M[5][2])  # 23: A prime number
model += is_square(M[5][5])  # 24: A square number
model += M[6][0] == M[5][3] // 17  # 25: 20 across divided by seventeen
model += M[7][0] == M[5][5] // 4  # 27: 6 down divided by four
model += M[7][7] == 4 * 12  # 28: Four dozen
model += M[8][0] == 7 * 144  # 29: Seven gross
model += M[8][5] == M[7][1] + 450  # 30: 22 down plus 450

# Down clues
model += M[1][0] == M[0][0] + 27  # 1: 1 across plus twenty-seven
model += M[1][1] == 5 * 12  # 2: Five dozen
model += M[1][8] == M[8][5] + 888  # 3: 30 across plus 888
model += M[3][3] == 2 * M[4][0]  # 4: Two times 17 across
model += M[4][4] == M[8][0] // 12  # 5: 29 across divided by twelve
model += M[5][5] == M[7][7] * M[5][2]  # 6: 28 across times 23 across
model += M[2][2] == M[1][2] + 4  # 10: 10 across plus four
model += M[2][6] == 3 * M[5][5]  # 12: Three times 24 across
model += M[3][1] == M[2][0] // 16  # 14: 13 across divided by sixteen
model += M[3][7] == M[7][7] * 15  # 16: 28 down times fifteen
model += M[4][1] == M[2][0] - 399  # 17: 13 across minus 399
model += M[7][1] == M[8][0] // 18  # 18: 29 across divided by eighteen
model += M[4][2] == M[7][1] - 94  # 19: 22 down minus ninety-four
model += M[4][6] == M[5][3] - 9  # 20: 20 across minus nine
model += M[4][7] == M[6][0] - 52  # 21: 25 across minus fifty-two
model += M[7][1] == M[4][6] * 6  # 22: 20 down times six
model += M[7][5] == 5 * M[5][5]  # 26: Five times 24 across
model += M[7][7] == M[4][7] + 27  # 28: 21 down plus twenty-seven

# Solve
model.solve()

# Print solution
solution = {"M": [row.value().tolist() for row in M]}
print(json.dumps(solution))