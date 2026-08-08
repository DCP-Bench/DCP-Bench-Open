
import cpmpy as cp
import json

# Model definition
model = cp.Model()

# Decision Variables
# x[i] = label (1..12) at position i (positions indexed 0..11)
x = cp.intvar(1, 12, shape=12, name="x")

# pos1 = index (0..11) of the card labeled 1
pos1 = cp.intvar(0, 11, name="pos1")

# Sequence of visited positions when starting at pos1:
# s[0] = pos1, s[t+1] = (s[t] + x[s[t]]) % 12
s = cp.intvar(0, 11, shape=12, name="s")

# Constraints

# x is a permutation of 1..12
model += cp.AllDifferent(x)

# pos1 points to the position holding label 1
# Since x is a permutation, exactly one index has value 1; enforcing x[pos1] == 1 links pos1 to that index.
model += (x[pos1] == 1)

# Walk recurrence and distinctness of the first 12 visited positions
model += (s[0] == pos1)
for t in range(11):
    # next position is current position plus the label at the current position, modulo 12
    model += (s[t + 1] == (s[t] + x[s[t]]) % 12)

# Ensure the first 12 visited positions are all different -> visits every position exactly once in these steps
model += cp.AllDifferent(s)

# Solve and print
if model.solve():
    solution = {'x': x.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
