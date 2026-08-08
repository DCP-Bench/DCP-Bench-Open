
import cpmpy as cp
import json

# Data
n = 12
# End of data

# Model definition
model = cp.Model()

# Decision Variables
# s is the sequence of pitch-classes (a permutation of 0..n-1)
s = cp.intvar(0, n - 1, shape=n, name="s")

# diffs is the sequence of intervals (absolute difference between neighbors)
diffs = cp.intvar(1, n - 1, shape=n - 1, name="diffs")

# Constraints
# s is a permutation of 0..n-1
model += cp.AllDifferent(s)

# diffs is a permutation of 1..n-1
model += cp.AllDifferent(diffs)

# intervals are absolute differences mod n (distances on the circle)
# According to the problem, difference = min(|s[i+1] - s[i]|, n - |s[i+1] - s[i]|)
# We must model for each i:
# diffs[i] = min(|s[i+1]-s[i]|, n - |s[i+1]-s[i]|)
# We use auxiliary variable diff_abs[i] = |s[i+1]-s[i]|
diff_abs = cp.intvar(0, n - 1, shape=n - 1, name="diff_abs")

for i in range(n - 1):
    # diff_abs[i] = |s[i+1] - s[i]|
    model += (diff_abs[i] == cp.Abs(s[i + 1] - s[i]))
    # diffs[i] = min(diff_abs[i], n - diff_abs[i])
    # Introduce boolean b[i] for which side is minimal
    b = cp.boolvar(name=f"b{i}")
    model += cp.IfThenElse(b, diffs[i] == diff_abs[i], diffs[i] == n - diff_abs[i])
    # diff_abs[i] cannot be zero because intervals are from 1..n-1
    model += (diff_abs[i] != 0)

# Symmetry breaking:
# Fix s[0] = 0 to avoid rotations of the solution
model += (s[0] == 0)
# And impose s[1] < s[n-1] to break reversal symmetry
model += (s[1] < s[n - 1])

# Solve and print
if model.solve():
    solution = {'x': s.value().tolist(), 'diffs': diffs.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
