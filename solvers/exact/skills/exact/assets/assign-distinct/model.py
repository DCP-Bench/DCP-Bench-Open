"""Satisfy: give four people four different desks, using one-hot indicators."""
from exact import Exact

PEOPLE = ["Ann", "Ben", "Cem", "Dora"]
DESKS = 4

solver = Exact()
# one-hot indicator y[p][d] == 1 exactly when person p sits at desk d
y = [[f"y_{p}_{d}" for d in range(DESKS)] for p in range(len(PEOPLE))]
seat = [f"seat_{p}" for p in range(len(PEOPLE))]
for p in range(len(PEOPLE)):
    solver.addVariable(seat[p], 0, DESKS - 1)
    for d in range(DESKS):
        solver.addVariable(y[p][d], 0, 1)
    # exactly one desk per person ...
    solver.addConstraint([(1, y[p][d]) for d in range(DESKS)], True, 1, True, 1)
    # ... and seat equals that desk
    solver.addConstraint([(d, y[p][d]) for d in range(DESKS)] + [(-1, seat[p])],
                         True, 0, True, 0)

# every desk is taken by exactly one person
for d in range(DESKS):
    solver.addConstraint([(1, y[p][d]) for p in range(len(PEOPLE))], True, 1, True, 1)

# Ann may not sit at desk 0
solver.addConstraint([(1, y[0][0])], True, 0, True, 0)

status = solver.runFull(optimize=False)
if status != "SAT":
    print("status:", status)
else:
    seats = solver.getLastSolutionFor(seat)
    print("status:", status)
    for name, desk in zip(PEOPLE, seats):
        print(f"{name} -> desk {desk}")
    print("all desks different:", len(set(seats)) == DESKS)
    print("Ann not at desk 0:", seats[0] != 0)
