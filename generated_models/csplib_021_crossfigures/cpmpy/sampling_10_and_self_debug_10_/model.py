
import cpmpy as cp
import json
from math import isqrt

# Grid specification from the problem description:
# Use strings to represent each cell: 'X' black, '_' white no printed number, or a printed clue number as string
grid_rows = [
    ["1","2","_","3","X","4","_","5","6"],
    ["7","_","X","8","_","_","X","9","_"],
    ["_","X","10","_","X","11","12","X","_"],
    ["13","14","_","_","X","15","_","16","_"],
    ["X","_","X","X","X","X","X","_","X"],
    ["17","_","18","19","X","20","21","_","22"],
    ["_","X","23","_","X","24","_","X","_"],
    ["25","26","X","27","_","_","X","28","_"],
    ["29","_","_","_","X","30","_","_","_"],
]

R = 9
C = 9

# Determine black cells and printed numbers
is_white = [[(grid_rows[r][c] != "X") for c in range(C)] for r in range(R)]
printed_label = [[None for _ in range(C)] for __ in range(R)]
for r in range(R):
    for c in range(C):
        val = grid_rows[r][c]
        if val != "X" and val != "_":
            printed_label[r][c] = int(val)

# Helper: find runs for across and down clues (only those with length >= 2 are considered clues)
across_starts = {}  # label -> (r,c,length)
down_starts = {}    # label -> (r,c,length)

# Across: start if white and (c==0 or left is black), and run length >= 2
for r in range(R):
    c = 0
    while c < C:
        if not is_white[r][c]:
            c += 1
            continue
        # start of a run at c
        start = c
        while c < C and is_white[r][c]:
            c += 1
        length = c - start
        if length >= 2:
            label = printed_label[r][start]
            if label is None:
                raise ValueError(f"Across run starting at {(r+1,start+1)} has no label in the grid.")
            across_starts[label] = (r, start, length)
# Down: similar, start if white and (r==0 or above is black)
for c in range(C):
    r = 0
    while r < R:
        if not is_white[r][c]:
            r += 1
            continue
        start = r
        while r < R and is_white[r][c]:
            r += 1
        length = r - start
        if length >= 2:
            label = printed_label[start][c]
            if label is None:
                raise ValueError(f"Down run starting at {(start+1,c+1)} has no label in the grid.")
            down_starts[label] = (start, c, length)

# Create digit variables for each cell: 0..9, black cells fixed to 0
digits = [[cp.intvar(0,9, name=f"d_{r+1}_{c+1}") for c in range(C)] for r in range(R)]
model = cp.Model()

for r in range(R):
    for c in range(C):
        if not is_white[r][c]:
            model += (digits[r][c] == 0)

# Create integer variables for each across and down clue, and link them to the digits
across_vars = {}
down_vars = {}

def concat_number_from_digits(dlist):
    # dlist: list of digit vars left-to-right
    L = len(dlist)
    coeffs = [10**(L-1-i) for i in range(L)]
    # Create a variable with bounds
    lb = 10**(L-1) if L > 1 else 0
    ub = 10**L - 1
    num = cp.intvar(lb, ub)
    # sum constraint (use cp.sum)
    expr = cp.sum([coeffs[i] * dlist[i] for i in range(L)])
    # Add constraints to the global model without using augmented assignment (avoid local assignment)
    model.add(num == expr)
    # enforce leading digit non-zero for L>1
    if L > 1:
        model.add(dlist[0] >= 1)
    return num

# Build across variables
for lbl, (r, c, length) in across_starts.items():
    dvars = [digits[r][c + i] for i in range(length)]
    across_vars[lbl] = concat_number_from_digits(dvars)

# Build down variables
for lbl, (r, c, length) in down_starts.items():
    dvars = [digits[r + i][c] for i in range(length)]
    down_vars[lbl] = concat_number_from_digits(dvars)

# Helper functions for primes and squares within a digit-length bound
def primes_in_range(lb, ub):
    res = []
    for n in range(lb, ub+1):
        if n < 2:
            continue
        is_p = True
        for k in range(2, isqrt(n)+1):
            if n % k == 0:
                is_p = False
                break
        if is_p:
            res.append(n)
    return res

def squares_in_range(lb, ub):
    res = []
    a = isqrt(lb)
    if a*a < lb:
        a += 1
    while a*a <= ub:
        res.append(a*a)
        a += 1
    return res

# Now add constraints according to the clue relations
A = across_vars
D = down_vars

# Across clues:
if 1 in A and 27 in A:
    model += (A[1] == 2 * A[27])

if 4 in A and 4 in D:
    model += (A[4] == D[4] + 71)

if 7 in A and 18 in D:
    model += (A[7] == D[18] + 4)

if 8 in A and 6 in D:
    model += (A[8] * 16 == D[6])

if 9 in A and 2 in D:
    model += (A[9] == D[2] - 18)

if 10 in A:
    model += (A[10] == 72)

if 11 in A and 5 in D:
    model += (A[11] == D[5] - 70)

if 13 in A and 26 in D and 23 in A:
    model += (A[13] == D[26] * A[23])

if 15 in A and 6 in D:
    model += (A[15] == D[6] - 350)

if 17 in A and 25 in A and 23 in A:
    model += (A[17] == A[25] * A[23])

if 20 in A:
    r,c,L = across_starts[20]
    lb = 10**(L-1) if L>1 else 0
    ub = 10**L - 1
    sqs = squares_in_range(lb, ub)
    if not sqs:
        raise ValueError("No squares in range for clue 20")
    model += cp.InDomain(A[20], sqs)

if 23 in A:
    r,c,L = across_starts[23]
    lb = 10**(L-1) if L>1 else 0
    ub = 10**L - 1
    primes = primes_in_range(lb, ub)
    if not primes:
        raise ValueError("No primes in range for clue 23")
    model += cp.InDomain(A[23], primes)

if 24 in A:
    r,c,L = across_starts[24]
    lb = 10**(L-1) if L>1 else 0
    ub = 10**L - 1
    sqs = squares_in_range(lb, ub)
    if not sqs:
        raise ValueError("No squares in range for clue 24")
    model += cp.InDomain(A[24], sqs)

if 25 in A and 20 in A:
    model += (A[25] * 17 == A[20])

if 27 in A and 6 in D:
    model += (A[27] * 4 == D[6])

if 28 in A:
    model += (A[28] == 48)

if 29 in A:
    model += (A[29] == 7 * 144)

if 30 in A and 22 in D:
    model += (A[30] == D[22] + 450)

# Down clues:
if 1 in D and 1 in A:
    model += (D[1] == A[1] + 27)

if 2 in D:
    model += (D[2] == 60)

if 3 in D and 30 in A:
    model += (D[3] == A[30] + 888)

if 4 in D and 17 in A:
    model += (D[4] == 2 * A[17])

if 5 in D and 29 in A:
    model += (D[5] * 12 == A[29])

if 6 in D and 28 in A and 23 in A:
    model += (D[6] == A[28] * A[23])

if 10 in D and 10 in A:
    model += (D[10] == A[10] + 4)

if 12 in D and 24 in A:
    model += (D[12] == 3 * A[24])

if 14 in D and 13 in A:
    model += (D[14] * 16 == A[13])

if 16 in D and 28 in D:
    model += (D[16] == D[28] * 15)

if 17 in D and 13 in A:
    model += (D[17] == A[13] - 399)

if 18 in D and 29 in A:
    model += (D[18] * 18 == A[29])

if 19 in D and 22 in D:
    model += (D[19] == D[22] - 94)

if 20 in D and 20 in A:
    model += (D[20] == A[20] - 9)

if 21 in D and 25 in A:
    model += (D[21] == A[25] - 52)

if 22 in D and 20 in D:
    model += (D[22] == D[20] * 6)

if 26 in D and 24 in A:
    model += (D[26] == 5 * A[24])

if 28 in D and 21 in D:
    model += (D[28] == D[21] + 27)

# Solve and print
if model.solve():
    M = [[0 for _ in range(C)] for __ in range(R)]
    for r in range(R):
        for c in range(C):
            M[r][c] = int(digits[r][c].value())
    solution = {'M': M}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
