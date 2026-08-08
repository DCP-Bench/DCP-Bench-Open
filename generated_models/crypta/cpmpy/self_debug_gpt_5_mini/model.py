
import cpmpy as cp
import json

# Data: the three numbers as sequences of letters (left-to-right)
top_str    = "BAIJJAJIIAHFCFEBBJEA"
second_str = "DHFGABCDIDBIFFAGFEJE"
res_str    = "GJEGACDDHFAFJBFIHEEF"

# Sanity check lengths
assert len(top_str) == len(second_str) == len(res_str)
n = len(top_str)  # number of columns (20)

# Create letter variables for A..J
letters = "A B C D E F G H I J".split()
letter_vars = {ch: cp.intvar(0, 9, name=ch) for ch in letters}

# Model
model = cp.Model()

# All letters different
model += cp.AllDifferent(list(letter_vars.values()))

# Leading letters cannot be zero: first letter of each number (leftmost)
model += (letter_vars['B'] != 0)
model += (letter_vars['D'] != 0)
model += (letter_vars['G'] != 0)

# Carries: c[0] is initial carry (0), c[n] is final carry (must be 0 because result has same length)
c = cp.intvar(0, 2, shape=n+1, name="c")
model += (c[0] == 0)
model += (c[n] == 0)

# Column-wise addition constraints (rightmost column is position n-1)
for j in range(n):
    pos = n - 1 - j  # index from leftmost = 0 to rightmost = n-1
    t = letter_vars[top_str[pos]]
    s = letter_vars[second_str[pos]]
    r = letter_vars[res_str[pos]]
    # t + s + carry_in = r + 10 * carry_out
    model += (t + s + c[j] == r + 10 * c[j+1])

# Solve
if model.solve():
    solution = {ch: int(letter_vars[ch].value()) for ch in letters}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
