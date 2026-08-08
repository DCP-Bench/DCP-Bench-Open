
import cpmpy as cp
import json

# Operations: index mapping
# 0: +2
# 1: /8  (exact division)
# 2: -3
# 3: *7

# Model definition
model = cp.Model()

# Decision Variables
# Ages (reasonable bounds)
m = cp.intvar(0, 1000, name="m")
h = cp.intvar(0, 1000, name="h")

# Intermediate values for 4 steps: v0..v4 (forward), w0..w4 (backward)
V = cp.intvar(0, 100000, shape=5, name="V")  # V[0]=m, V[4]=h
W = cp.intvar(0, 100000, shape=5, name="W")  # W[0]=h, W[4]=m

# Link endpoints
model += (V[0] == m)
model += (V[4] == h)
model += (W[0] == h)
model += (W[4] == m)

# Permutation indicators: bijf for forward, bijb for backward
bijf = cp.boolvar(shape=(4, 4), name="bijf")
bijb = cp.boolvar(shape=(4, 4), name="bijb")

# Each position uses exactly one operation; each operation used exactly once
for i in range(4):
    model += (cp.sum(bijf[i, :]) == 1)
    model += (cp.sum(bijb[i, :]) == 1)
for j in range(4):
    model += (cp.sum(bijf[:, j]) == 1)
    model += (cp.sum(bijb[:, j]) == 1)

# Forward step constraints
for i in range(4):
    # op 0: +2
    model += bijf[i, 0].implies(V[i+1] == V[i] + 2)
    # op 1: /8  -> V[i] == V[i+1] * 8  (ensures exact division)
    model += bijf[i, 1].implies(V[i] == V[i+1] * 8)
    # op 2: -3
    model += bijf[i, 2].implies(V[i+1] == V[i] - 3)
    # op 3: *7
    model += bijf[i, 3].implies(V[i+1] == V[i] * 7)

# Backward step constraints (starting from h to get m)
for i in range(4):
    # op 0: +2
    model += bijb[i, 0].implies(W[i+1] == W[i] + 2)
    # op 1: /8  -> W[i] == W[i+1] * 8
    model += bijb[i, 1].implies(W[i] == W[i+1] * 8)
    # op 2: -3
    model += bijb[i, 2].implies(W[i+1] == W[i] - 3)
    # op 3: *7
    model += bijb[i, 3].implies(W[i+1] == W[i] * 7)

# Ensure the two orders are different (permutations not identical)
diffs = []
for i in range(4):
    for j in range(4):
        # bijf[i,j] != bijb[i,j] yields a boolean; sum of these >= 1 ensures difference
        diffs.append(bijf[i, j] != bijb[i, j])
model += (cp.sum(diffs) >= 1)

# Optional: ages should be positive (realistic)
model += (m >= 1)
model += (h >= 1)

# Solve and print
if model.solve():
    solution = {'m': int(m.value()), 'h': int(h.value())}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
