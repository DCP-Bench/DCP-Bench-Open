"""All optimal answers: choose 3 distinct values in 0..4 with x0 < x1, maximising
x0 + x1 + x2. Step 1 proves the optimum; step 2 rebuilds the model without the
objective, pins the optimum and enumerates."""
from pycsp3 import *


def build():
    x = VarArray(size=3, dom=range(5), id="x")
    satisfy(
        # the three values are distinct
        AllDifferent(x),
        # the first value is below the second
        x[0] < x[1],
    )
    return x, x[0] + x[1] + x[2]


x, score = build()
maximize(score)
if solve() is not OPTIMUM:
    raise SystemExit("optimum not proven")
best = bound()
print("Optimum:", best)

clear()                      # drop every variable, constraint and the objective
x, score = build()
satisfy(score == best)       # pin the optimum, no objective
status = solve(sols=ALL)
count = len(x[0].values) if status is SAT else 0
for k in range(count):
    print(values(x, sol=k))
print("Optimal solutions:", count)
