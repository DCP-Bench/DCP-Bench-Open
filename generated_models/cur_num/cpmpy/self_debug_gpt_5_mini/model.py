
import cpmpy as cp
import json

# Model definition
model = cp.Model()

# Decision Variables
# 'peculiar' is the number we want (between 1 and 10000)
peculiar = cp.intvar(1, 10000, name="peculiar")

# We'll avoid nonlinear variable*variable by using Element constraints:
# a_idx selects the sqrt (a) for peculiar+1 = a^2, where a in 1..100
a_idx = cp.intvar(0, 100-1, name="a_idx")
asq_map = [(i+1)*(i+1) for i in range(100)]  # a^2 values for a=1..100
asq = cp.intvar(1, 10001, name="asq")  # will hold a^2

# b_idx selects the sqrt (b) for peculiar/2 + 1 = b^2, where b in 1..71
b_idx = cp.intvar(0, 71-1, name="b_idx")
bsq_map = [(i+1)*(i+1) for i in range(71)]  # b^2 values for b=1..71
bsq = cp.intvar(1, 71*71, name="bsq")  # will hold b^2

# Constraints
model += cp.Element(asq_map, a_idx) == asq
model += cp.Element(bsq_map, b_idx) == bsq

# peculiar = 2*(b^2 - 1)
model += peculiar == 2 * (bsq - 1)

# peculiar + 1 = a^2
model += peculiar + 1 == asq

# Exclude the known example 48, look for another one
model += peculiar != 48

# Ensure peculiar in range (domain already enforces this)
# Solve
if model.solve():
    solution = {'peculiar': int(peculiar.value())}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
