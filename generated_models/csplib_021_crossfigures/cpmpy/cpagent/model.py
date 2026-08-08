import cpmpy as cp
import numpy as np
import json

# Step 1: Deconstruct & Pre-compute
# This is a crossfigure puzzle - numerical crossword with mathematical clues
# Grid is 9x9 with blocked cells (X) and numbered cells for clues
# Need to identify all across and down slots and their constraints

# Grid layout (-1 = blocked, 0 = empty, >0 = numbered)
grid = [
    [1, 2, 0, 3, -1, 4, 0, 5, 6],     # row 0
    [7, 0, -1, 8, 0, 0, -1, 9, 0],    # row 1  
    [0, -1, 10, 0, -1, 11, 12, -1, 0], # row 2
    [13, 14, 0, 0, -1, 15, 0, 16, 0], # row 3
    [-1, 0, -1, -1, -1, -1, -1, 0, -1], # row 4
    [17, 0, 18, 19, -1, 20, 21, 0, 22], # row 5
    [0, -1, 23, 0, -1, 24, 0, -1, 0], # row 6
    [25, 26, -1, 27, 0, 0, -1, 28, 0], # row 7
    [29, 0, 0, 0, -1, 30, 0, 0, 0]    # row 8
]

def find_slots(grid):
    """Find all across and down slots in the grid"""
    rows, cols = len(grid), len(grid[0])
    across_slots = {}
    down_slots = {}
    
    # Find across slots
    for r in range(rows):
        current_slot = []
        start_num = None
        for c in range(cols):
            if grid[r][c] == -1:  # blocked
                if len(current_slot) >= 2:
                    across_slots[start_num] = current_slot.copy()
                current_slot = []
                start_num = None
            else:
                if grid[r][c] > 0 and start_num is None:
                    start_num = grid[r][c]
                current_slot.append((r, c))
        
        if len(current_slot) >= 2:
            across_slots[start_num] = current_slot.copy()
    
    # Find down slots  
    for c in range(cols):
        current_slot = []
        start_num = None
        for r in range(rows):
            if grid[r][c] == -1:  # blocked
                if len(current_slot) >= 2:
                    down_slots[start_num] = current_slot.copy()
                current_slot = []
                start_num = None
            else:
                if grid[r][c] > 0 and start_num is None:
                    start_num = grid[r][c]
                current_slot.append((r, c))
        
        if len(current_slot) >= 2:
            down_slots[start_num] = current_slot.copy()
    
    return across_slots, down_slots

def get_perfect_squares(min_val, max_val):
    """Get all perfect squares in range"""
    squares = []
    i = 1
    while i * i <= max_val:
        if i * i >= min_val:
            squares.append(i * i)
        i += 1
    return squares

def get_primes(min_val, max_val):
    """Get all primes in range using sieve"""
    if max_val < 2:
        return []
    
    sieve = [True] * (max_val + 1)
    sieve[0] = sieve[1] = False
    
    for i in range(2, int(max_val**0.5) + 1):
        if sieve[i]:
            for j in range(i*i, max_val + 1, i):
                sieve[j] = False
    
    return [i for i in range(min_val, max_val + 1) if sieve[i]]

# Find all slots
across_slots, down_slots = find_slots(grid)

# Step 2: Model with CPMpy
model = cp.Model()

# Create variables for each slot
slot_vars = {}

# For across slots
for num, positions in across_slots.items():
    length = len(positions)
    min_val = 10**(length-1)
    max_val = 10**length - 1
    slot_vars[f'across_{num}'] = cp.intvar(min_val, max_val, name=f'across_{num}')

# For down slots  
for num, positions in down_slots.items():
    length = len(positions)
    min_val = 10**(length-1)
    max_val = 10**length - 1
    slot_vars[f'down_{num}'] = cp.intvar(min_val, max_val, name=f'down_{num}')

# Create digit variables for each cell
digit_vars = {}
for r in range(9):
    for c in range(9):
        if grid[r][c] != -1:  # not blocked
            digit_vars[(r,c)] = cp.intvar(0, 9, name=f'digit_{r}_{c}')

# Add constraints that link slot values to digit values
for num, positions in across_slots.items():
    length = len(positions)
    digit_sum = 0
    for i, (r, c) in enumerate(positions):
        place_value = 10**(length - 1 - i)
        digit_sum += digit_vars[(r,c)] * place_value
    model += slot_vars[f'across_{num}'] == digit_sum

for num, positions in down_slots.items():
    length = len(positions)
    digit_sum = 0
    for i, (r, c) in enumerate(positions):
        place_value = 10**(length - 1 - i)
        digit_sum += digit_vars[(r,c)] * place_value
    model += slot_vars[f'down_{num}'] == digit_sum

# Add fixed value constraints
model += slot_vars['across_10'] == 72    # Dozen in six gross = (6*144)/12 = 72
model += slot_vars['down_2'] == 60       # Five dozen = 5 * 12 = 60
model += slot_vars['across_28'] == 48    # Four dozen = 4 * 12 = 48
model += slot_vars['across_29'] == 1008  # Seven gross = 7 * 144 = 1008

# Add relational constraints - Across
model += slot_vars['across_1'] == slot_vars['across_27'] * 2
model += slot_vars['across_4'] == slot_vars['down_4'] + 71
model += slot_vars['across_7'] == slot_vars['down_18'] + 4
model += slot_vars['across_8'] == slot_vars['down_6'] // 16
model += slot_vars['across_9'] == slot_vars['down_2'] - 18
model += slot_vars['across_11'] == slot_vars['down_5'] - 70
model += slot_vars['across_13'] == slot_vars['down_26'] * slot_vars['across_23']
model += slot_vars['across_15'] == slot_vars['down_6'] - 350
model += slot_vars['across_17'] == slot_vars['across_25'] * slot_vars['across_23']
model += slot_vars['across_25'] == slot_vars['across_20'] // 17
model += slot_vars['across_27'] == slot_vars['down_6'] // 4
model += slot_vars['across_30'] == slot_vars['down_22'] + 450

# Add relational constraints - Down
model += slot_vars['down_1'] == slot_vars['across_1'] + 27
model += slot_vars['down_3'] == slot_vars['across_30'] + 888
model += slot_vars['down_4'] == slot_vars['across_17'] * 2
model += slot_vars['down_5'] == slot_vars['across_29'] // 12
model += slot_vars['down_6'] == slot_vars['across_28'] * slot_vars['across_23']
model += slot_vars['down_10'] == slot_vars['across_10'] + 4
model += slot_vars['down_12'] == slot_vars['across_24'] * 3
model += slot_vars['down_14'] == slot_vars['across_13'] // 16
model += slot_vars['down_16'] == slot_vars['down_28'] * 15
model += slot_vars['down_17'] == slot_vars['across_13'] - 399
model += slot_vars['down_18'] == slot_vars['across_29'] // 18
model += slot_vars['down_19'] == slot_vars['down_22'] - 94
model += slot_vars['down_20'] == slot_vars['across_20'] - 9
model += slot_vars['down_21'] == slot_vars['across_25'] - 52
model += slot_vars['down_22'] == slot_vars['down_20'] * 6
model += slot_vars['down_26'] == slot_vars['across_24'] * 5
model += slot_vars['down_28'] == slot_vars['down_21'] + 27

# Add square and prime constraints
squares_20 = get_perfect_squares(1000, 9999)  # 4-digit squares
primes_23 = get_primes(10, 99)                # 2-digit primes  
squares_24 = get_perfect_squares(10, 99)      # 2-digit squares

model += cp.Table([slot_vars['across_20']], [(s,) for s in squares_20])
model += cp.Table([slot_vars['across_23']], [(p,) for p in primes_23])  
model += cp.Table([slot_vars['across_24']], [(s,) for s in squares_24])

# Step 3: Solve & Verify
if model.solve():
    # Extract the solution grid
    solution_grid = [[-1 if grid[r][c] == -1 else 0 for c in range(9)] for r in range(9)]
    
    # Fill in the solved digits
    for (r, c), var in digit_vars.items():
        solution_grid[r][c] = var.value()
    
    # Convert to output format (0 for blocked cells)
    M = []
    for r in range(9):
        row = []
        for c in range(9):
            if solution_grid[r][c] == -1:
                row.append(0)  # Use 0 for blocked cells in output
            else:
                row.append(solution_grid[r][c])
        M.append(row)
    
    # Step 4: Output
    print(json.dumps({"M": M}))
else:
    print(json.dumps({"error": "No solution found"}))