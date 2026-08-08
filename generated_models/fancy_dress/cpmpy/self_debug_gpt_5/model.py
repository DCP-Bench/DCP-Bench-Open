
import cpmpy as cp
import json

# Model definition
model = cp.Model()

# Decision Variables (0/1)
t = cp.boolvar(name="t")  # tie
h = cp.boolvar(name="h")  # hat
r = cp.boolvar(name="r")  # shirt
s = cp.boolvar(name="s")  # socks
n = cp.boolvar(name="n")  # entrance fee

# Violation indicators for rules 1-3
v1 = cp.boolvar(name="v1")  # violation of rule 1: t -> r
v2 = cp.boolvar(name="v2")  # violation of rule 2: (s & r) -> (t | h)
v3 = cp.boolvar(name="v3")  # violation of rule 3: (r | h | ~s) -> t

# Constraints:
# Define violations
model += (v1 == (t & ~r))
model += (v2 == (s & r & ~(t | h)))
model += (v3 == ((r | h | ~s) & ~t))

# Entrance fee iff any rule is violated
model += (n == (v1 | v2 | v3))

# Objective: minimize total cost
# Costs: tie $10, hat $2, shirt $0 (owned), socks $12, entrance fee $11
total_cost = 10*t + 2*h + 12*s + 11*n
model.minimize(total_cost)

# Solve and print
if model.solve():
    solution = {
        't': int(t.value()),
        'h': int(h.value()),
        'r': int(r.value()),
        's': int(s.value()),
        'n': int(n.value())
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
