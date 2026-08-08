
import cpmpy as cp
import json

# Input data
names = ["Agatha herself", "the butler", "Charles"]
# End of input data

# Model definition
model = cp.Model()

# Decision Variables
# hates[i][j] = 1 if person i hates person j, else 0
hates = cp.intvar(0, 1, shape=(3, 3), name="hates")
# wealth ranking: higher number means richer
w = cp.intvar(0, 2, shape=3, name="w")
# killer index: 0 = Agatha, 1 = butler, 2 = Charles
killer = cp.intvar(0, 2, name="killer")

# Constraints

# 1) The killer always hates his victim (Aunt Agatha is person 0)
model += hates[killer, 0] == 1
#    and is no richer than his victim
model += w[killer] <= w[0]

# 2) Charles (person 2) hates no one that Agatha hates
for j in range(3):
    model += hates[2, j] + hates[0, j] <= 1

# 3) Agatha (person 0) hates everybody except the butler (person 1)
#    She may also hate herself (to allow self-murder)
model += hates[0, 1] == 0    # does not hate the butler
model += hates[0, 0] == 1    # hates herself
model += hates[0, 2] == 1    # hates Charles

# 4) The butler (person 1) hates everyone not richer than Aunt Agatha
for j in range(3):
    model += cp.implies(w[j] <= w[0], hates[1, j] == 1)

#    and also hates everyone whom Agatha hates
for j in range(3):
    model += cp.implies(hates[0, j] == 1, hates[1, j] == 1)

# 5) No one hates everyone (i.e., sum of hates[i,*] < 3)
for i in range(3):
    model += cp.sum(hates[i, :]) <= 2

# Solve and print
if model.solve():
    solution = {'killer': int(killer.value())}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
