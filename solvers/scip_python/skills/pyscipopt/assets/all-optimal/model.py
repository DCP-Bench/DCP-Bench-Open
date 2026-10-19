# Every optimal solution: pay 10 with as few coins of value 2, 3, 5 and 7 as possible,
# and list every coin mix that reaches that minimum.
# Step 1 proves the optimum; step 2 pins the objective variable to it and enumerates
# with no-goods over general integers (two indicator binaries per variable).
from pyscipopt import Model, quicksum

coins = [2, 3, 5, 7]
amount = 10

m = Model("coins")
m.hideOutput()
count = [m.addVar(vtype="I", lb=0, ub=amount // c, name=f"n{c}") for c in coins]
m.addCons(quicksum(c * x for c, x in zip(coins, count)) == amount)
# objective held in a bounded integer variable, so it can be pinned afterwards
total = m.addVar(vtype="I", lb=0, ub=amount, name="total")
m.addCons(total == quicksum(count))
m.setObjective(total, "minimize")

m.optimize()
if m.getStatus() != "optimal":
    raise SystemExit(f"Status: {m.getStatus()}")
best = round(m.getVal(total))
print("Fewest coins:", best)

m.freeTransform()
m.addCons(total == best)         # pin the proven optimum
m.setObjective(0, "minimize")    # nothing left to optimise: plain enumeration

mixes = []
while True:
    m.optimize()
    status = m.getStatus()
    if status == "infeasible":       # no further optimal solution: the list is complete
        break
    if status != "optimal":          # any other status: the list would be incomplete
        raise SystemExit(f"Stopped early: {status}")
    values = [round(m.getVal(x)) for x in count]
    mixes.append(values)
    m.freeTransform()
    # no-good over integers: some x must leave its value v, i.e. x <= v-1 or x >= v+1
    moves = []
    for x, v in zip(count, values):
        if v > x.getLbOriginal():
            lo = m.addVar(vtype="B")
            m.addConsIndicator(x <= v - 1, binvar=lo)   # always pass binvar
            moves.append(lo)
        if v < x.getUbOriginal():
            hi = m.addVar(vtype="B")
            m.addConsIndicator(x >= v + 1, binvar=hi)
            moves.append(hi)
    m.addCons(quicksum(moves) >= 1)

for values in mixes:
    print(" + ".join(f"{n}x{c}" for c, n in zip(coins, values) if n))
print("Optimal solutions:", len(mixes))
