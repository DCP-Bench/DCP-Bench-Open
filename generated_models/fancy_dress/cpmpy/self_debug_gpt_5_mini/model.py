
import cpmpy as cp
import json

# Decision variables: tie (t), hat (h), shirt (r), socks (s), entrance fee (n)
t = cp.boolvar(name="t")
h = cp.boolvar(name="h")
r = cp.boolvar(name="r")
s = cp.boolvar(name="s")
n = cp.boolvar(name="n")

# Model definition
model = cp.Model()

# Mr Greenguest owns a green shirt
model += (r == 1)

# Rules encoded as logical constraints (we will relate them to the entrance fee variable)
# Rule 1: If someone wears a green tie he has to wear a green shirt.  t -> r  ===  (~t | r)
rule1 = (~t | r)

# Rule 2: A guest may only wear green socks and a green shirt if he wears a green tie or a green hat.
# (s & r) -> (t | h)  ===  (~(s & r) | t | h)
rule2 = (~(s & r) | t | h)

# Rule 3: A guest wearing a green shirt or a green hat or who does not wear green socks must wear a green tie.
# (r | h | ~s) -> t  ===  (~(r | h | ~s) | t)
rule3 = (~(r | h | ~s) | t)

# Entrance fee (n) must be true iff the guest is NOT dressed according to rules 1-3.
all_rules_hold = rule1 & rule2 & rule3
model += (n == ~all_rules_hold)

# Costs:
# tie $10, hat $2, shirt $0 (he already owns it), socks $12, entrance fee $11
total_cost = cp.sum([10 * t, 2 * h, 0 * r, 12 * s, 11 * n])

# Objective: minimize total cost
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
