from ortools.sat.python import cp_model
import json

# Model definition
model = cp_model.CpModel()

# We have clues for across and down numbers.
# The grid is 9x9, with some black cells (X) where no number is placed.
# The clues are numbered and correspond to certain cells.

# We will create variables for each clue number (across and down).
# The clues are:
# Across: 1,4,7,8,9,10,11,13,15,17,20,23,24,25,27,28,29,30
# Down: 1,2,3,4,5,6,10,12,14,16,17,18,19,20,21,22,26,28

# Create variables for all clues (across and down)
# We assume all clues are positive integers.

# Across clues
across_nums = [1,4,7,8,9,10,11,13,15,17,20,23,24,25,27,28,29,30]
across = {}
for num in across_nums:
    across[num] = model.NewIntVar(1, 1000000, f'across_{num}')

# Down clues
down_nums = [1,2,3,4,5,6,10,12,14,16,17,18,19,20,21,22,26,28]
down = {}
for num in down_nums:
    down[num] = model.NewIntVar(1, 1000000, f'down_{num}')

# Now add constraints from the clues:

# Across clues:
# 1: 27 across times two
model.Add(across[1] == across[27] * 2)
# 4: 4 down plus seventy-one
model.Add(across[4] == down[4] + 71)
# 7: 18 down plus four
model.Add(across[7] == down[18] + 4)
# 8: 6 down divided by sixteen
model.Add(across[8] * 16 == down[6])
# 9: 2 down minus eighteen
model.Add(across[9] == down[2] - 18)
# 10: Dozen in six gross
# Six gross = 6 * 144 = 864
# Dozen in six gross = 864 / 12 = 72
model.Add(across[10] == 72)
# 11: 5 down minus seventy
model.Add(across[11] == down[5] - 70)
# 13: 26 down times 23 across
model.Add(across[13] == down[26] * across[23])
# 15: 6 down minus 350
model.Add(across[15] == down[6] - 350)
# 17: 25 across times 23 across
model.Add(across[17] == across[25] * across[23])
# 20: A square number
# We'll constrain it later after domain reduction
# For now, just keep domain
# 23: A prime number
# We'll constrain it later
# 24: A square number
# We'll constrain it later
# 25: 20 across divided by seventeen
model.Add(across[25] * 17 == across[20])
# 27: 6 down divided by four
model.Add(across[27] * 4 == down[6])
# 28: Four dozen = 48
model.Add(across[28] == 48)
# 29: Seven gross = 7 * 144 = 1008
model.Add(across[29] == 1008)
# 30: 22 down plus 450
model.Add(across[30] == down[22] + 450)

# Down clues:
# 1: 1 across plus twenty-seven
model.Add(down[1] == across[1] + 27)
# 2: Five dozen = 60
model.Add(down[2] == 60)
# 3: 30 across plus 888
model.Add(down[3] == across[30] + 888)
# 4: Two times 17 across
model.Add(down[4] == 2 * across[17])
# 5: 29 across divided by twelve
model.Add(down[5] * 12 == across[29])
# 6: 28 across times 23 across
model.Add(down[6] == across[28] * across[23])
# 10: 10 across plus four
model.Add(down[10] == across[10] + 4)
# 12: Three times 24 across
model.Add(down[12] == 3 * across[24])
# 14: 13 across divided by sixteen
model.Add(down[14] * 16 == across[13])
# 16: 28 down times fifteen
model.Add(down[16] == down[28] * 15)
# 17: 13 across minus 399
model.Add(down[17] == across[13] - 399)
# 18: 29 across divided by eighteen
model.Add(down[18] * 18 == across[29])
# 19: 22 down minus ninety-four
model.Add(down[19] == down[22] - 94)
# 20: 20 across minus nine
model.Add(down[20] == across[20] - 9)
# 21: 25 across minus fifty-two
model.Add(down[21] == across[25] - 52)
# 22: 20 down times six
model.Add(down[22] == down[20] * 6)
# 26: Five times 24 across
model.Add(down[26] == 5 * across[24])
# 28: 21 down plus twenty-seven
model.Add(down[28] == down[21] + 27)

# Additional constraints for prime and square numbers:

# Helper function to add prime constraint
def add_prime_constraint(model, var):
    # We will limit domain to reasonable range and check primality by enumeration
    # Let's limit domain to 2..1000 for prime clues
    # We'll create a table of primes in that range
    primes = [
        2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97,
        101,103,107,109,113,127,131,137,139,149,151,157,163,167,173,179,181,191,
        193,197,199,211,223,227,229,233,239,241,251,257,263,269,271,277,281,283,
        293,307,311,313,317,331,337,347,349,353,359,367,373,379,383,389,397,401,
        409,419,421,431,433,439,443,449,457,461,463,467,479,487,491,499,503,509,
        521,523,541,547,557,563,569,571,577,587,593,599,601,607,613,617,619,631,
        641,643,647,653,659,661,673,677,683,691,701,709,719,727,733,739,743,751,
        757,761,769,773,787,797,809,811,821,823,827,829,839,853,857,859,863,877,
        881,883,887,907,911,919,929,937,941,947,953,967,971,977,983,991,997
    ]
    model.AddAllowedAssignments([var], [(p,) for p in primes])

# Helper function to add square number constraint
def add_square_constraint(model, var):
    # Limit domain to 1..1000000
    # We'll create a variable s for the root and constrain var = s*s
    s = model.NewIntVar(1, 1000, f'sqrt_{var.Name()}')
    model.AddMultiplicationEquality(var, [s, s])

# Apply prime constraint to across 23
add_prime_constraint(model, across[23])

# Apply square constraints to across 20 and 24
add_square_constraint(model, across[20])
add_square_constraint(model, across[24])

# Now, from the grid, we can deduce the length of each clue (number of digits)
# and impose domain restrictions accordingly.

# The grid numbering and clue lengths (from the grid and clues):

# Across clues and their lengths (number of digits):
# 1 across: length 2 (cells 1,2)
# 4 across: length 2 (cells 4,5)
# 7 across: length 2 (cells 7,8)
# 8 across: length 1 (cell 8)
# 9 across: length 2 (cells 9,10)
# 10 across: length 2 (cells 10,11)
# 11 across: length 2 (cells 11,12)
# 13 across: length 2 (cells 13,14)
# 15 across: length 2 (cells 15,16)
# 17 across: length 2 (cells 17,18)
# 20 across: length 2 (cells 20,21)
# 23 across: length 2 (cells 23,24)
# 24 across: length 2 (cells 24,25)
# 25 across: length 1 (cell 25)
# 27 across: length 2 (cells 27,28)
# 28 across: length 2 (cells 28,29)
# 29 across: length 3 (cells 29,30,31)
# 30 across: length 3 (cells 30,31,32)

# From the grid, the actual clue lengths are:
# 1 across: 2 digits
# 4 across: 2 digits
# 7 across: 2 digits
# 8 across: 1 digit
# 9 across: 2 digits
# 10 across: 2 digits
# 11 across: 2 digits
# 13 across: 2 digits
# 15 across: 2 digits
# 17 across: 2 digits
# 20 across: 2 digits
# 23 across: 2 digits
# 24 across: 2 digits
# 25 across: 1 digit
# 27 across: 2 digits
# 28 across: 2 digits
# 29 across: 3 digits
# 30 across: 3 digits

# We will constrain the domain of each clue accordingly:
def constrain_length(var, length):
    # length is number of digits
    # min = 10^(length-1), max = 10^length - 1
    min_val = 10**(length-1)
    max_val = 10**length - 1
    model.Add(var >= min_val)
    model.Add(var <= max_val)

# Apply length constraints for across clues
constrain_length(across[1], 2)
constrain_length(across[4], 2)
constrain_length(across[7], 2)
constrain_length(across[8], 1)
constrain_length(across[9], 2)
constrain_length(across[10], 2)
constrain_length(across[11], 2)
constrain_length(across[13], 2)
constrain_length(across[15], 2)
constrain_length(across[17], 2)
constrain_length(across[20], 2)
constrain_length(across[23], 2)
constrain_length(across[24], 2)
constrain_length(across[25], 1)
constrain_length(across[27], 2)
constrain_length(across[28], 2)
constrain_length(across[29], 3)
constrain_length(across[30], 3)

# Down clues length constraints (from grid and clue lengths):
# 1 down: 2 digits
# 2 down: 2 digits
# 3 down: 3 digits
# 4 down: 3 digits
# 5 down: 2 digits
# 6 down: 4 digits
# 10 down: 2 digits
# 12 down: 3 digits
# 14 down: 2 digits
# 16 down: 3 digits
# 17 down: 3 digits
# 18 down: 2 digits
# 19 down: 3 digits
# 20 down: 2 digits
# 21 down: 2 digits
# 22 down: 3 digits
# 26 down: 3 digits
# 28 down: 3 digits

constrain_length(down[1], 2)
constrain_length(down[2], 2)
constrain_length(down[3], 3)
constrain_length(down[4], 3)
constrain_length(down[5], 2)
constrain_length(down[6], 4)
constrain_length(down[10], 2)
constrain_length(down[12], 3)
constrain_length(down[14], 2)
constrain_length(down[16], 3)
constrain_length(down[17], 3)
constrain_length(down[18], 2)
constrain_length(down[19], 3)
constrain_length(down[20], 2)
constrain_length(down