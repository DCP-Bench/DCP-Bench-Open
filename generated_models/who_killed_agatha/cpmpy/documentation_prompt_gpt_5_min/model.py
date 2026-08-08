
import cpmpy as cp
import json

# Data
names = ["Agatha herself", "the butler", "Charles"]
n = 3
# End of data

# Model definition
model = cp.Model()

# Decision Variables
# H[i,j] is True iff person i hates person j
H = cp.boolvar(shape=(n, n), name="H")

# wealth of each person (0..2 is enough to express relative comparisons)
wealth = cp.intvar(0, 2, shape=n, name="wealth")

# killer index (0-based: 0=Agatha,1=butler,2=Charles)
killer = cp.intvar(0, n - 1, name="killer")

# Constraints

# Agatha hates everybody except the butler.
model += (H[0, 0] == 1)  # Agatha hates herself
model += (H[0, 1] == 0)  # Agatha does not hate the butler
model += (H[0, 2] == 1)  # Agatha hates Charles

# Charles hates noone that Agatha hates.
for j in range(n):
    model += H[0, j].implies(~H[2, j])

# The butler hates everyone whom Agatha hates.
for j in range(n):
    model += H[0, j].implies(H[1, j])

# The butler hates everyone not richer than Aunt Agatha.
for j in range(n):
    model += (wealth[j] <= wealth[0]).implies(H[1, j])

# Noone hates everyone.
for i in range(n):
    model += cp.sum(H[i, :]) <= n - 1

# A killer always hates, and is no richer than his victim (Agatha).
# killer hates Agatha:
model += cp.Element([H[0, 0], H[1, 0], H[2, 0]], killer) == 1
# killer is no richer than Agatha:
model += cp.Element(list(wealth), killer) <= wealth[0]

# Solve and print
if model.solve():
    solution = {'killer': int(killer.value())}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
