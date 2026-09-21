# Match participants to cars they want, as many matches as possible.
from dcp_pb import Pb


def build(instance):
    possible = instance["possible_assignments"]
    participants = len(possible)
    cars = len(possible[0])

    pb = Pb()
    assignments = pb.bool_grid(participants, cars)
    for i in range(participants):
        for j in range(cars):
            if possible[i][j] == 0:
                pb.eq([(1, assignments[i][j])], 0)
        pb.at_most(assignments[i], 1)
    for j in range(cars):
        pb.at_most([assignments[i][j] for i in range(participants)], 1)

    pb.maximise([(1, flag) for row in assignments for flag in row])
    return pb, {"assignments": assignments}
