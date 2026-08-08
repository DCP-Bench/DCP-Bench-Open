
import cpmpy as cp
import json

# Grid tokens as in the problem statement.
# Each row is a list of tokens: 'X' = black cell, '_' = white cell (no printed clue number)
# or a numeric string means a white cell with a clue number printed there (start of some clue).
rows = [
    ["1","2","_","3","X","4","_","5","6"],
    ["7","_","X","8","_","_","X","9","_"],
    ["_","X","10","_","X","11","12","X","_"],
    ["13","14","_","_","X","15","_","16","_"],
    ["X","_","X","X","X","X","X","_","X"],
    ["17","_","18","19","X","20","21","_","22"],
    ["_","X","23","_","X","24","_","X","_"],
    ["25","26","X","27","_","_","X","28","_"],
    ["29","_","_","_","X","30","_","_","_"]
]

n = 9
# Build boolean mask for blacks and track printed clue numbers
is_black = [[(rows[r][c] == "X") for c in range(n)] for r in range(n)]
printed_number = [[None if rows[r][c] in ("X","_") else int(rows[r][c]) for c in range(n)] for r in range(n)]

# Find horizontal (across) runs of length >= 2: record start cell, length, and clue number if any
across_slots = {}   # clue_number -> (r,c,length)
for r in range(n):
    c = 0
    while c < n:
        if not is_black[r][c]:
            # start of a run?
            start = c
            while c < n and not is_black[r][c]:
                c += 1
            length = c - start
            if length >= 2:
                # determine clue number: if printed_number at start exists, use it.
                num = printed_number[r][start]
                # It is possible that a run starts at a cell without a printed number in the input,
                # but according to the puzzle the clues correspond to printed numbers. We'll only
                # keep runs where the start cell has a printed clue number.
                if num is None:
                    raise RuntimeError(f"Across run at row {r+1}, col {start+1} length {length} has no printed clue number.")
                across_slots[num] = (r, start, length)
        else:
            c += 1

# Find vertical (down) runs of length >= 2: record start cell, length, and clue number if any
down_slots = {}  # clue_number -> (r,c,length)
for c in range(n):
    r = 0
    while r < n:
        if not is_black[r][c]:
            start = r
            while r < n and not is_black[r][c]:
                r += 1
            length = r - start
            if length >= 2:
                num = printed_number[start][c]
                if num is None:
                    raise RuntimeError(f"Down run at row {start+1}, col {c+1} length {length} has no printed clue number.")
                down_slots[num] = (start, c, length)
        else:
            r += 1

# The clues as parsed from the problem statement
# We'll create shorthand maps A# and D# for across and down integer variables.
# Create model and decision variables

model = cp.Model()

# Digit variables: 9x9 intvars 0..9; for black cells fixed to 0.
digits = cp.intvar(0, 9, shape=(n, n), name="digits")
for r in range(n):
    for c in range(n):
        if is_black[r][c]:
            model += (digits[r, c] == 0)

# Create across and down integer variables for each slot found.
across_vars = {}
for num, (r, c0, L) in across_slots.items():
    lo = 10 ** (L - 1)
    hi = 10 ** L - 1
    across_vars[num] = cp.intvar(lo, hi, name=f"A{num}")

down_vars = {}
for num, (r0, c, L) in down_slots.items():
    lo = 10 ** (L - 1)
    hi = 10 ** L - 1
    down_vars[num] = cp.intvar(lo, hi, name=f"D{num}")

# Link across/down integer variables to digits
for num, (r, c0, L) in across_slots.items():
    var = across_vars[num]
    coeffs = [10 ** (L - 1 - k) for k in range(L)]
    expr = cp.sum([digits[r, c0 + k] * coeffs[k] for k in range(L)])
    model += (var == expr)
    # Leading digit >= 1
    model += (digits[r, c0] >= 1)

for num, (r0, c, L) in down_slots.items():
    var = down_vars[num]
    coeffs = [10 ** (L - 1 - k) for k in range(L)]
    expr = cp.sum([digits[r0 + k, c] * coeffs[k] for k in range(L)])
    model += (var == expr)
    # Leading digit >= 1
    model += (digits[r0, c] >= 1)

# For convenience, create helper to get A# and D# variables (or raise if missing)
def A(num):
    if num not in across_vars:
        raise RuntimeError(f"Across clue {num} not found in parsed slots.")
    return across_vars[num]

def D(num):
    if num not in down_vars:
        raise RuntimeError(f"Down clue {num} not found in parsed slots.")
    return down_vars[num]

# Now add the arithmetic clues exactly as given in the problem statement.

# Across clues
# 1  : 27 across times two
model += (A(1) == 2 * A(27))
# 4  : 4 down plus seventy-one
model += (A(4) == D(4) + 71)
# 7  : 18 down plus four
model += (A(7) == D(18) + 4)
# 8  : 6 down divided by sixteen  => A8 * 16 == D6
model += (A(8) * 16 == D(6))
# 9  : 2 down minus eighteen
model += (A(9) == D(2) - 18)
# 10 : Dozen in six gross -> six gross = 6*144 = 864 dozens = 864/12 = 72
model += (A(10) == 72)
# 11 : 5 down minus seventy
model += (A(11) == D(5) - 70)
# 13 : 26 down times 23 across
model += (A(13) == D(26) * A(23))
# 15 : 6 down minus 350
model += (A(15) == D(6) - 350)
# 17 : 25 across times 23 across
model += (A(17) == A(25) * A(23))
# 20 : A square number
# 23 : A prime number
# 24 : A square number
# 25 : 20 across divided by seventeen => A20 == A25 * 17
model += (A(20) == A(25) * 17)
# 27 : 6 down divided by four => A27 * 4 == D6
model += (A(27) * 4 == D(6))
# 28 : Four dozen = 48
model += (A(28) == 48)
# 29 : Seven gross = 7 * 144 = 1008
model += (A(29) == 1008)
# 30 : 22 down plus 450
model += (A(30) == D(22) + 450)

# Down clues
# 1 : 1 across plus twenty-seven
model += (D(1) == A(1) + 27)
# 2 : Five dozen = 60
model += (D(2) == 60)
# 3 : 30 across plus 888
model += (D(3) == A(30) + 888)
# 4 : Two times 17 across
model += (D(4) == 2 * A(17))
# 5 : 29 across divided by twelve => D5 * 12 == A29
model += (D(5) * 12 == A(29))
# 6 : 28 across times 23 across
model += (D(6) == A(28) * A(23))
# 10 : 10 across plus four
model += (D(10) == A(10) + 4)
# 12 : Three times 24 across
model += (D(12) == 3 * A(24))
# 14 : 13 across divided by sixteen => D14 * 16 == A13
model += (D(14) * 16 == A(13))
# 16 : 28 down times fifteen
model += (D(16) == D(28) * 15)
# 17 : 13 across minus 399
model += (D(17) == A(13) - 399)
# 18 : 29 across divided by eighteen => D18 * 18 == A29
model += (D(18) * 18 == A(29))
# 19 : 22 down minus ninety-four
model += (D(19) == D(22) - 94)
# 20 : 20 across minus nine
model += (D(20) == A(20) - 9)
# 21 : 25 across minus fifty-two
model += (D(21) == A(25) - 52)
# 22 : 20 down times six
model += (D(22) == D(20) * 6)
# 26 : Five times 24 across
model += (D(26) == 5 * A(24))
# 28 : 21 down plus twenty-seven
model += (D(28) == D(21) + 27)

# Now handle special domain restrictions: primes and squares for specific across clues.

# Helper: create integer lists of primes and squares in a given inclusive range
def primes_in_range(lo, hi):
    lo = max(2, lo)
    sieve = [True] * (hi + 1)
    for p in range(2, int(hi**0.5) + 1):
        if sieve[p]:
            for multiple in range(p*p, hi+1, p):
                sieve[multiple] = False
    return [i for i in range(lo, hi+1) if sieve[i]]

def squares_in_range(lo, hi):
    res = []
    start = int((lo - 1) ** 0.5) + 1
    v = start * start
    while v <= hi:
        if v >= lo:
            res.append(v)
        start += 1
        v = start * start
    return res

# A23 is prime
r23, c23, L23 = across_slots[23]
lo23 = 10 ** (L23 - 1)
hi23 = 10 ** L23 - 1
primes23 = primes_in_range(lo23, hi23)
if not primes23:
    raise RuntimeError("No primes exist in range for A23")
model += cp.InDomain(A(23), primes23)

# A20 and A24 are square numbers
for num in (20, 24):
    r, c, L = across_slots[num]
    lo = 10 ** (L - 1)
    hi = 10 ** L - 1
    squares = squares_in_range(lo, hi)
    if not squares:
        raise RuntimeError(f"No squares exist in range for A{num}")
    model += cp.InDomain(A(num), squares)

# Divisibility constraints already set as multiplied equality (no fractional division used).

# Solve the model
if model.solve():
    # Build M: 0 for black cells, digit for white cells
    M = [[0]*n for _ in range(n)]
    for r in range(n):
        for c in range(n):
            M[r][c] = int(digits[r, c].value())
    solution = {'M': M}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
