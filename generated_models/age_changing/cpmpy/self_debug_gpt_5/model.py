
import cpmpy as cp
import json

# Model definition
model = cp.Model()

# Decision Variables
m = cp.intvar(1, 120, name="m")  # my age
h = cp.intvar(1, 120, name="h")  # husband's age

# Permutations of operations: 0:+2, 1:/8, 2:-3, 3:*7
perm1 = cp.intvar(0, 3, shape=4, name="perm1")  # order starting from m to get h
perm2 = cp.intvar(0, 3, shape=4, name="perm2")  # order starting from h to get m

# States after each of the 4 operations (5 states including start)
s1 = cp.intvar(-2000, 2000, shape=5, name="s1")
s2 = cp.intvar(-2000, 2000, shape=5, name="s2")

# Constraints
# Ages different (natural assumption) and bounds already set
model += (m != h)

# Each permutation uses each operation exactly once
model += cp.AllDifferent(perm1)
model += cp.AllDifferent(perm2)

# The two orders are different
model += cp.any([perm1[i] != perm2[i] for i in range(4)])

# Link start and end states
model += (s1[0] == m)
model += (s1[4] == h)
model += (s2[0] == h)
model += (s2[4] == m)

# Apply operations according to perm1 on s1
for i in range(4):
    model += (perm1[i] == 0).implies(s1[i+1] == s1[i] + 2)     # +2
    model += (perm1[i] == 1).implies(8 * s1[i+1] == s1[i])     # /8, exact division
    model += (perm1[i] == 2).implies(s1[i+1] == s1[i] - 3)     # -3
    model += (perm1[i] == 3).implies(s1[i+1] == 7 * s1[i])     # *7

# Apply operations according to perm2 on s2
for i in range(4):
    model += (perm2[i] == 0).implies(s2[i+1] == s2[i] + 2)     # +2
    model += (perm2[i] == 1).implies(8 * s2[i+1] == s2[i])     # /8, exact division
    model += (perm2[i] == 2).implies(s2[i+1] == s2[i] - 3)     # -3
    model += (perm2[i] == 3).implies(s2[i+1] == 7 * s2[i])     # *7

# Solve and print
if model.solve():
    solution = {'m': int(m.value()), 'h': int(h.value())}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
