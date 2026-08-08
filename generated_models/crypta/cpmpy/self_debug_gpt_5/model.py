
import cpmpy as cp
import json

# Data
top_str = "BAIJJAJIIAHFCFEBBJEA"
bottom_str = "DHFGABCDIDBIFFAGFEJE"
sum_str = "GJEGACDDHFAFJBFIHEEF"

letters = ['A','B','C','D','E','F','G','H','I','J']
idx = {ch:i for i,ch in enumerate(letters)}

# Convert strings to index lists
top_idx = [idx[ch] for ch in top_str]
bottom_idx = [idx[ch] for ch in bottom_str]
sum_idx = [idx[ch] for ch in sum_str]

n = len(top_idx)  # number of digits

# Model definition
model = cp.Model()

# Decision Variables
x = cp.intvar(0, 9, shape=len(letters), name="x")  # digits for A..J
carry = cp.intvar(0, 1, shape=n+1, name="carry")   # carry[0..n], carry in/out per column

# Constraints
# All letters map to distinct digits
model += cp.AllDifferent(x)

# No leading zeros on the three numbers
model += (x[idx['B']] != 0)
model += (x[idx['D']] != 0)
model += (x[idx['G']] != 0)

# Carry-in at least significant digit is 0, and final carry-out is 0 (since lengths are equal)
model += (carry[0] == 0)
model += (carry[n] == 0)

# Column-wise addition constraints from rightmost (least significant) to leftmost
for k in range(n):
    # process from rightmost: position from right is k
    ti = top_idx[n-1-k]
    bi = bottom_idx[n-1-k]
    si = sum_idx[n-1-k]
    model += (x[ti] + x[bi] + carry[k] == x[si] + 10*carry[k+1])

# Solve and print
if model.solve():
    solution = {
        'A': int(x[idx['A']].value()),
        'B': int(x[idx['B']].value()),
        'C': int(x[idx['C']].value()),
        'D': int(x[idx['D']].value()),
        'E': int(x[idx['E']].value()),
        'F': int(x[idx['F']].value()),
        'G': int(x[idx['G']].value()),
        'H': int(x[idx['H']].value()),
        'I': int(x[idx['I']].value()),
        'J': int(x[idx['J']].value())
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
