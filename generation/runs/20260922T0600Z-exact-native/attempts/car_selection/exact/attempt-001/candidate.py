# Match participants to cars they want, as many matches as possible.
from exact import Exact


def build(instance):
    possible = instance["possible_assignments"]
    participants = len(possible)
    cars = len(possible[0])

    solver = Exact()
    assignments = [[f"a{i}_{j}" for j in range(cars)] for i in range(participants)]
    for row in assignments:
        for name in row:
            solver.addVariable(name, 0, 1)
    for i in range(participants):
        for j in range(cars):
            if possible[i][j] == 0:
                solver.addConstraint([(1, assignments[i][j])], True, 0, True, 0)
        solver.addConstraint([(1, name) for name in assignments[i]],
                             False, 0, True, 1)
    for j in range(cars):
        solver.addConstraint([(1, assignments[i][j]) for i in range(participants)],
                             False, 0, True, 1)

    matched = [(1, name) for row in assignments for name in row]
    return solver, {"assignments": assignments}, ("maximize", matched)
