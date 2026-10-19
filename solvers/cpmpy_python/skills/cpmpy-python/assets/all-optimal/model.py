"""Every optimal choice of three talks, when several choices share the best rating."""
import cpmpy as cp

rating = [8, 8, 7, 6, 8, 5]
minutes = [40, 45, 30, 35, 50, 25]
BUDGET = 120

pick = cp.boolvar(shape=len(rating), name="pick")
constraints = [
    cp.sum(pick) == 3,
    cp.sum([m * p for m, p in zip(minutes, pick)]) <= BUDGET,
]
total_rating = cp.sum([r * p for r, p in zip(rating, pick)])

# 1. Find the optimum on a model that carries the objective.
search = cp.Model(constraints)
search.maximize(total_rating)
search.solve()
best = int(search.objective_value())

# 2. Post the optimum as a constraint on a model WITHOUT an objective (solveAll rejects one
#    under OR-Tools) and enumerate every choice that reaches it.
optimal = []
count = cp.Model(constraints + [total_rating == best]).solveAll(
    display=lambda: optimal.append(tuple(i for i in range(len(rating)) if pick[i].value())))

print("Optimum:", best)
print("Optimal choices:", count)
for choice in sorted(optimal):
    print("  talks", ", ".join(str(i + 1) for i in choice))
