# Enumerate every subset of 1..6 whose values sum to 7.
from hermax.model import Model

VALUES = list(range(1, 7))
TARGET = 7

m = Model()
pick = m.bool_vector("pick", len(VALUES))  # the decision variables to enumerate
m &= (sum(v * pick[i] for i, v in enumerate(VALUES)) == TARGET)

solutions = []
while True:
    r = m.solve()
    if r.status != "sat":  # "unsat": no further solution
        break
    chosen = tuple(bool(flag) for flag in r[pick])
    solutions.append(chosen)
    # Forbid exactly this assignment of the decision variables, then solve again.
    block = None
    for var, value in zip(pick, chosen):
        literal = ~var if value else var
        block = literal if block is None else (block | literal)
    m &= block

for chosen in solutions:
    print([v for v, flag in zip(VALUES, chosen) if flag])
print(f"{len(solutions)} subsets")
