
import cpmpy as cp
import json

# The grid is 9x9, with some cells blocked (X).
# We will model the variables for each clue number (across and down).
# The clues are interdependent equations.

# Clues:
# Across:
#  1: 27 across * 2
#  4: 4 down + 71
#  7: 18 down + 4
#  8: 6 down / 16
#  9: 2 down - 18
# 10: Dozen in six gross (6 gross = 6*144=864, dozen in 864 = 864/12=72)
# 11: 5 down - 70
# 13: 26 down * 23 across
# 15: 6 down - 350
# 17: 25 across * 23 across
# 20: A square number
# 23: A prime number
# 24: A square number
# 25: 20 across / 17
# 27: 6 down / 4
# 28: Four dozen (48)
# 29: Seven gross (7*144=1008)
# 30: 22 down + 450

# Down:
#  1: 1 across + 27
#  2: Five dozen (60)
#  3: 30 across + 888
#  4: 2 * 17 across
#  5: 29 across / 12
#  6: 28 across * 23 across
# 10: 10 across + 4
# 12: 3 * 24 across
# 14: 13 across / 16
# 16: 28 down * 15
# 17: 13 across - 399
# 18: 29 across / 18
# 19: 22 down - 94
# 20: 20 across - 9
# 21: 25 across - 52
# 22: 20 down * 6
# 26: 5 * 24 across
# 28: 21 down + 27

# We will create integer variables for each clue number.
# We will assume all clues are positive integers.
# We will add constraints according to the clues.

# Variables for Across clues (1 to 30)
across_vars = {}
for i in [1,4,7,8,9,10,11,13,15,17,20,23,24,25,27,28,29,30]:
    across_vars[i] = cp.intvar(1, 20000, name=f"A{i}")

# Variables for Down clues (1 to 28)
down_vars = {}
for i in [1,2,3,4,5,6,10,12,14,16,17,18,19,20,21,22,26,28]:
    down_vars[i] = cp.intvar(1, 20000, name=f"D{i}")

model = cp.Model()

A = across_vars
D = down_vars

# Given constants:
# 10 across = dozen in six gross = 864/12=72
model += (A[10] == 72)
# 28 across = four dozen = 48
model += (A[28] == 48)
# 29 across = seven gross = 7*144=1008
model += (A[29] == 1008)
# 2 down = five dozen = 60
model += (D[2] == 60)

# Now the clues:

# Across clues:
model += (A[1] == A[27] * 2)
model += (A[4] == D[4] + 71)
model += (A[7] == D[18] + 4)
model += (A[8] * 16 == D[6])  # 8 = 6 down / 16 => 6 down = 8*16
model += (A[9] == D[2] - 18)
model += (A[11] == D[5] - 70)
model += (A[13] == D[26] * A[23])
model += (A[15] == D[6] - 350)
model += (A[17] == A[25] * A[23])
# 20 across is a square number
# 24 across is a square number
# 23 across is a prime number
# 25 across = 20 across / 17
model += (A[25] * 17 == A[20])
model += (A[27] * 4 == D[6])
model += (A[30] == D[22] + 450)

# 28 across = 48 (already set)
# 29 across = 1008 (already set)

# Down clues:
model += (D[1] == A[1] + 27)
model += (D[3] == A[30] + 888)
model += (D[4] == 2 * A[17])
model += (D[5] * 12 == A[29])
model += (D[6] == A[28] * A[23])
model += (D[10] == A[10] + 4)
model += (D[12] == 3 * A[24])
model += (D[14] * 16 == A[13])
model += (D[16] == D[28] * 15)
model += (D[17] == A[13] - 399)
model += (D[18] * 18 == A[29])
model += (D[19] == D[22] - 94)
model += (D[20] == A[20] - 9)
model += (D[21] == A[25] - 52)
model += (D[22] == D[20] * 6)
model += (D[26] == 5 * A[24])
model += (D[28] == D[21] + 27)

# Additional constraints for prime and square numbers:

# Prime number check for A[23]
# We will limit the prime to be between 2 and 20000
def is_prime(n):
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    r = int(n**0.5)
    for i in range(3, r+1, 2):
        if n % i == 0:
            return False
    return True

# We cannot directly enforce primality in CP, but we can enumerate primes up to 20000
# and use a table constraint.

# Generate primes up to 20000
primes = []
for num in range(2, 20001):
    # Use a simple sieve or primality test
    # For speed, use a simple sieve here
    # But since this is code generation, we do a simple test
    # To speed up, we can use a sieve approach:
    # But here, just do a simple test:
    # To avoid long code, we do a simple sieve:
    pass

# Implement sieve of Eratosthenes for primes up to 20000
max_prime = 20000
sieve = [True]*(max_prime+1)
sieve[0] = False
sieve[1] = False
for i in range(2, int(max_prime**0.5)+1):
    if sieve[i]:
        for j in range(i*i, max_prime+1, i):
            sieve[j] = False
primes = [i for i in range(2, max_prime+1) if sieve[i]]

model += cp.Table([A[23]], [[p] for p in primes])

# Square numbers for A[20] and A[24]
# We can model A[20] = s20^2 and A[24] = s24^2 for some integer variables s20, s24
s20 = cp.intvar(1, 150, name="s20")  # 150^2=22500 > 20000, safe upper bound
s24 = cp.intvar(1, 150, name="s24")
model += (A[20] == s20 * s20)
model += (A[24] == s24 * s24)

# Now, the grid has numbers in some cells, we must assign the values of clues to the grid cells.
# The grid is 9x9, with some blocked cells (X).
# The clues correspond to sequences of cells horizontally or vertically.

# We will create a 9x9 matrix M with 0 for blocked cells and variables for others.
# The clues are placed on the grid as per the problem statement.

# Grid layout with clue numbers and blocked cells:
# Row 1:  2 _ 3 X 4 _ 5 6
# Row 2: 7 _ X 8 _ _ X 9 _
# Row 3: _ X 10 _ X 11 12 X _
# Row 4: 13 14 _ _ X 15 _ 16 _
# Row 5: X _ X X X X X _ X
# Row 6: 17 _ 18 19 X 20 21 _ 22
# Row 7: _ X 23 _ X 24 _ X _
# Row 8: 25 26 X 27 _ _ X 28 _
# Row 9: 29 _ _ _ X 30 _ _ _

# We will create a 9x9 matrix M with 0 for blocked cells and variables for others.
# For each clue, we will assign the digits of the clue value to the corresponding cells.

# First, create M with 0 for blocked cells and variables for others.
# We will create integer variables for each cell that is not blocked.
# The domain is 0-9 for each cell (digits).

# Blocked cells coordinates (0-based):
blocked = {(0,4),(1,2),(1,6),(2,1),(2,4),(2,7),(3,4),(4,0),(4,2),(4,3),(4,4),(4,5),(4,6),(4,8),
           (5,4),(6,1),(6,4),(6,7),(7,2),(7,6),(8,4)}

M = []
for r in range(9):
    row = []
    for c in range(9):
        if (r,c) in blocked:
            row.append(0)
        else:
            row.append(cp.intvar(0,9, name=f"M_{r}_{c}"))
    M.append(row)

# Now, assign digits of clues to the grid cells.
# We need to know the length and positions of each clue on the grid.

# From the grid and clue numbers, we can deduce the positions and lengths:

# Across clues:
# 1 across: cells with clue number 1 across: row 0, col 0-? (from grid)
# From the grid:
# Row 0:  1  2  _  3  X  4  _  5  6
# Clues across are numbered at the start of the word:
# Across clues start at:
# 1 across: row 0, col 0 to col 1 (cells 1 and 2)
# 4 across: row 0, col 5 to col 8 (cells 4, _, 5, 6)
# 7 across: row 1, col 0 to col 1 (7, _)
# 8 across: row 1, col 3 to col 5 (8, _, _)
# 9 across: row 1, col 7 to col 8 (9, _)
# 10 across: row 2, col 2 to col 2 (10)
# 11 across: row 2, col 5 to col 6 (11, 12)
# 13 across: row 3, col 0 to col 1 (13, 14)
# 15 across: row 3, col 5 to col 6 (15, _)
# 17 across: row 5, col 0 to col 1 (17, _)
# 18 across: row 5, col 2 to col 3 (18, 19)
# 20 across: row 5, col 5 to col 6 (20, 21)
# 23 across: row 6, col 2 to col 2 (23)
# 24 across: row 6, col 5 to col 5 (24)
# 25 across: row 7, col 0 to col 1 (25, 26)
# 27 across: row 7, col 3 to col 4 (27, _)
# 28 across: row 7, col 7 to col 7 (28)
# 29 across: row 8, col 0 to col 3 (29, _, _, _)
# 30 across: row 8, col 5 to col 8 (30, _, _, _)

# Down clues:
# 1 down: col 0, row 0 to row 3 (1,7,_,13)
# 2 down: col 1, row 0 to row 1 (2, _)
# 3 down: col 2, row 2 to row 8 (10, _, 23, _, 27, _, _)
# 4 down: col 3, row 0 to row 3 (3,8, _, _)
# 5 down: col 