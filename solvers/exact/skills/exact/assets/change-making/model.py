"""Minimise: fewest coins that pay exactly 23 with coins of 1, 4 and 6."""
from exact import Exact

AMOUNT = 23
COINS = {"coin_1": 1, "coin_4": 4, "coin_6": 6}
NAMES = list(COINS)

solver = Exact()
for name in NAMES:
    solver.addVariable(name, 0, AMOUNT // COINS[name])
solver.addConstraint([(value, name) for name, value in COINS.items()],
                     True, AMOUNT, True, AMOUNT)

coins_used = [(1, name) for name in NAMES]
solver.setObjective(coins_used, minimize=True)

state, value = solver.toOptimum()
if state == "SAT":
    counts = solver.getLastSolutionFor(NAMES)
    print("status:", state)
    print("Minimum coins:", value)
    print("counts:", dict(zip(NAMES, counts)))
else:
    print("status:", state)
