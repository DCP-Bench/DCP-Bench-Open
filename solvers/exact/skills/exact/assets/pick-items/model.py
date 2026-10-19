"""All optimal solutions: choose exactly two of six items, maximising value.

Solve for the optimum, pin the objective at that value, then enumerate.
Exact minimises internally, so a maximisation returns the negated optimum.
"""
from exact import Exact

VALUES = [4, 4, 3, 2, 4, 1]
PICK = 2
ITEMS = [f"item_{i}" for i in range(len(VALUES))]
objective = list(zip(VALUES, ITEMS))

solver = Exact()
for name in ITEMS:
    solver.addVariable(name, 0, 1)
solver.addConstraint([(1, name) for name in ITEMS], True, PICK, True, PICK)
solver.setObjective(objective, minimize=False)

state, negated = solver.toOptimum()
if state != "SAT":
    print("no proven optimum:", state)
else:
    best = -negated  # the returned value is negated for maximisation
    print("Optimal value:", best)
    # pin the objective at its proven optimum, then enumerate
    solver.addConstraint(objective, True, best, True, best)
    optimal = []
    while solver.runFull(optimize=False) == "SAT":
        optimal.append(solver.getLastSolutionFor(ITEMS))
        solver.invalidateLastSol(ITEMS)
    print("Optimal solutions:", len(optimal))
    for chosen in optimal:
        print("chosen:", [i for i, bit in enumerate(chosen) if bit])
