"""Every minimum-cost set cover: enumerate optimal solutions with RC2 and blocking clauses."""
from itertools import combinations

from pysat.examples.rc2 import RC2Stratified
from pysat.formula import IDPool, WCNF

ELEMENTS = range(6)
SETS = {  # name: (elements covered, cost)
    "S0": ({0, 1, 2}, 1),
    "S1": ({3, 4, 5}, 2),
    "S2": ({0, 3}, 1),
    "S3": ({1, 4}, 1),
    "S4": ({2, 5}, 1),
    "S5": (set(ELEMENTS), 5),
}
names = list(SETS)

pool = IDPool()
pick = {name: pool.id(("pick", name)) for name in names}

wcnf = WCNF()
for e in ELEMENTS:                                  # hard: every element is covered
    wcnf.append([pick[n] for n in names if e in SETS[n][0]])
for name in names:                                  # soft: pay the cost of each chosen set
    wcnf.append([-pick[name]], weight=SETS[name][1])

rc2 = RC2Stratified(wcnf, solver="glucose42")
optimum, optimal = None, []
while True:
    model = rc2.compute()
    if model is None:
        break
    if optimum is None:
        optimum = rc2.cost
    elif rc2.cost > optimum:                        # the next answer is worse: stop
        break
    true_lits = {lit for lit in model if lit > 0}
    chosen = tuple(name for name in names if pick[name] in true_lits)
    optimal.append(chosen)
    # Block this choice of sets so the next model differs in the chosen sets.
    rc2.add_clause([-pick[n] if n in chosen else pick[n] for n in names])
rc2.delete()

print("Optimum:", optimum)
for chosen in optimal:
    print("optimal cover:", ", ".join(chosen))
print("Number of optimal covers:", len(optimal))
brute = [c for k in range(len(names) + 1) for c in combinations(names, k)
         if set().union(*(SETS[n][0] for n in c)) == set(ELEMENTS)]
best = min(sum(SETS[n][1] for n in c) for c in brute)
print("Matches brute force:", sorted(optimal) == sorted(c for c in brute if sum(SETS[n][1] for n in c) == best))
