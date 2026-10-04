# Car selection: assign participants to cars they are interested in, at most
# one car per participant and one participant per car, maximising the number
# of assignments.
from pysat.card import CardEnc, EncType
from pysat.formula import IDPool, WCNF


def build(instance):
    possible = instance["possible_assignments"]
    n_participants = len(possible)
    n_cars = len(possible[0])

    pool = IDPool()
    # assignments[i][j] is true when participant i gets car j.
    assignments = [[pool.id(("assign", i, j)) for j in range(n_cars)]
                   for i in range(n_participants)]

    formula = WCNF()

    # A participant can only be assigned a car they are interested in.
    for i in range(n_participants):
        for j in range(n_cars):
            if not possible[i][j]:
                formula.append([-assignments[i][j]])

    # Each participant is assigned to at most one car.
    for i in range(n_participants):
        formula.extend(CardEnc.atmost(lits=assignments[i], bound=1, vpool=pool,
                                      encoding=EncType.seqcounter).clauses)

    # Each car is assigned to at most one participant.
    for j in range(n_cars):
        column = [assignments[i][j] for i in range(n_participants)]
        formula.extend(CardEnc.atmost(lits=column, bound=1, vpool=pool,
                                      encoding=EncType.seqcounter).clauses)

    # Maximise the number of assignments: every possible pair left unassigned
    # pays 1, so the cost is the shortfall from the number of possible pairs.
    for i in range(n_participants):
        for j in range(n_cars):
            if possible[i][j]:
                formula.append([assignments[i][j]], weight=1)

    return formula, {"assignments": assignments}
