# Match participants to cars they want, as many matches as possible.
from hermax.model import Model


def build(instance):
    possible = instance["possible_assignments"]
    participants = len(possible)
    cars = len(possible[0])

    m = Model()
    assignments = m.bool_matrix("assignments", participants, cars)
    for i in range(participants):
        for j in range(cars):
            if possible[i][j] == 0:
                m &= ~assignments[i][j]
        m &= assignments.row(i).at_most_one()
    for j in range(cars):
        m &= assignments.col(j).at_most_one()

    # Maximising the matches: every pairing left unmade costs one.
    for i in range(participants):
        for j in range(cars):
            if possible[i][j]:
                m.obj[1] += assignments[i][j]
    return m, {"assignments": assignments}
