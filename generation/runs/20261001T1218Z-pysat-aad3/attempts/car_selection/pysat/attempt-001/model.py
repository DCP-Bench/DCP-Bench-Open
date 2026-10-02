# Car selection: match participants to the cars they are interested in, at most one car per
# participant and one participant per car, so that as many participants as possible get a car.
# PySAT only decides satisfiability, so the number of assignments to maximise is returned as
# the objective (the runner refuses a returned objective instead of ignoring it).
from pysat.card import CardEnc, EncType
from pysat.formula import CNF, IDPool


def build(instance):
    possible = instance["possible_assignments"]  # possible[i][j] = 1 if participant i likes car j
    n_participants = len(possible)
    n_cars = len(possible[0])

    pool = IDPool()
    cnf = CNF()
    # assignments[i][j] is true when participant i gets car j
    assignments = [[pool.id(("assign", i, j)) for j in range(n_cars)] for i in range(n_participants)]

    # a participant only gets a car they are interested in
    for i in range(n_participants):
        for j in range(n_cars):
            if not possible[i][j]:
                cnf.append([-assignments[i][j]])
    # each participant gets at most one car
    for i in range(n_participants):
        cnf.extend(CardEnc.atmost(lits=assignments[i], bound=1, vpool=pool,
                                  encoding=EncType.seqcounter).clauses)
    # each car goes to at most one participant
    for j in range(n_cars):
        cnf.extend(CardEnc.atmost(lits=[assignments[i][j] for i in range(n_participants)], bound=1,
                                  vpool=pool, encoding=EncType.seqcounter).clauses)

    total = [lit for row in assignments for lit in row]
    return cnf, {"assignments": assignments}, ("maximize", total)
