# Match participants to cars they want, as many matches as possible.
from dcp_maxsat import MaxSat


def build(instance):
    possible = instance["possible_assignments"]
    participants = len(possible)
    cars = len(possible[0])

    sat = MaxSat()
    assignments = sat.bool_grid(participants, cars)
    for i in range(participants):
        for j in range(cars):
            if possible[i][j] == 0:
                sat.clause([-assignments[i][j]])
        sat.at_most(assignments[i], 1)
    for j in range(cars):
        sat.at_most([assignments[i][j] for i in range(participants)], 1)

    flat = [lit for row in assignments for lit in row]
    matched = sat.int(0, min(participants, cars))
    sat.link_count(flat, matched)
    return sat, {"assignments": assignments}, ("maximize", matched)
