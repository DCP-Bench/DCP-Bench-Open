# Kidney exchange: people on a waiting list can donate a kidney to some compatible people. Choose
# the transplants so that anyone who gives a kidney also receives one, nobody gives or receives
# more than one, and as many people as possible receive a new kidney.
from exact import Exact


def build(instance):
    num_people = instance["num_people"]
    compatible = instance["compatible"]  # compatible[i] = people (1-based) that person i can donate to
    n = num_people

    solver = Exact()

    # transplants[i][j] = 1 if person i donates to person j. A donation that is not compatible is
    # not possible, so that variable is fixed to 0 (its domain is 0..0).
    transplants = [[f"transplant_{i}_{j}" for j in range(n)] for i in range(n)]
    for i in range(n):
        for j in range(n):
            solver.addVariable(transplants[i][j], 0, 1 if (j + 1) in compatible[i] else 0)

    for i in range(n):
        gives = [(1, transplants[i][j]) for j in range(n)]
        receives = [(1, transplants[j][i]) for j in range(n)]
        # each person can donate to at most one person and receive from at most one person
        solver.addConstraint(gives, False, 0, True, 1)
        solver.addConstraint(receives, False, 0, True, 1)
        # anyone who gives a kidney must receive one: since gives is 0 or 1, gives <= receives
        solver.addConstraint(gives + [(-c, name) for c, name in receives], False, 0, True, 0)

    # maximise the number of transplants
    return (solver, {"transplants": transplants},
            ("maximize", [(1, transplants[i][j]) for i in range(n) for j in range(n)]))
