"""All solutions: count the ways to pay 12 with coins of 1, 2 and 5.

The total number of coins is an auxiliary variable; enumeration blocks each
solution only on the coin counts, so it is not counted twice.
"""
from exact import Exact

AMOUNT = 12
COINS = {"a": 1, "b": 2, "c": 5}  # counts of 1-, 2- and 5-coins
COUNTS = list(COINS)

solver = Exact()
for name in COUNTS:
    solver.addVariable(name, 0, AMOUNT // COINS[name])
solver.addVariable("total_coins", 0, AMOUNT)
solver.addConstraint([(value, name) for name, value in COINS.items()],
                     True, AMOUNT, True, AMOUNT)
solver.addConstraint([(1, name) for name in COUNTS] + [(-1, "total_coins")],
                     True, 0, True, 0)

solutions = []
while solver.runFull(optimize=False) == "SAT":
    solutions.append(solver.getLastSolutionFor(COUNTS))
    # block this solution projected onto the declared variables only
    solver.invalidateLastSol(COUNTS)

print("Solutions:", len(solutions))
for counts in solutions:
    print(dict(zip(COUNTS, counts)))
