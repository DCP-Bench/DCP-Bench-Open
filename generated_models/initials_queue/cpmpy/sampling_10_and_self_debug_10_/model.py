
import cpmpy as cp
import json

# The 10 possible ordered-in-alphabet pairs from letters A..E (0..4)
# Enumerated as:
# 0: AB (0,1)
# 1: AC (0,2)
# 2: AD (0,3)
# 3: AE (0,4)
# 4: BC (1,2)
# 5: BD (1,3)
# 6: BE (1,4)
# 7: CD (2,3)
# 8: CE (2,4)
# 9: DE (3,4)
first_letters  = [0, 0, 0, 0, 1, 1, 1, 2, 2, 3]
second_letters = [1, 2, 3, 4, 2, 3, 4, 3, 4, 4]

# Model definition
model = cp.Model()

# Decision Variables: idx[p] is which of the 10 pairs is at position p (0..9)
idx = cp.intvar(0, 9, shape=10, name="idx")

# All pairs are used exactly once (a permutation)
model += cp.AllDifferent(idx)

# Given: BE at front (index 6), CD right behind (index 7), BD at end (index 5)
model += (idx[0] == 6)
model += (idx[1] == 7)
model += (idx[9] == 5)

# No adjacent people share a letter: for each adjacent pair, their letters are disjoint
for p in range(9):
    f1 = cp.Element(first_letters, idx[p])
    s1 = cp.Element(second_letters, idx[p])
    f2 = cp.Element(first_letters, idx[p+1])
    s2 = cp.Element(second_letters, idx[p+1])
    # Enforce no equality between any letter of position p and any letter of position p+1
    model += (f1 != f2)
    model += (f1 != s2)
    model += (s1 != f2)
    model += (s1 != s2)

# Solve and print
if model.solve():
    idx_sol = idx.value().tolist()
    queue = [[first_letters[i], second_letters[i]] for i in idx_sol]
    solution = {'queue': queue}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
