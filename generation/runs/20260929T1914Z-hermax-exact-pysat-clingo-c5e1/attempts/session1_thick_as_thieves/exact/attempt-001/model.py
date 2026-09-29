# Thick as thieves: six suspects, at most two of them guilty. The innocent tell
# the truth and the guilty lie in what they said.
from exact import Exact

SUSPECTS = ["artie", "bill", "crackitt", "dodgy", "edgy", "fingers"]


def build(instance):
    # The puzzle is fixed by the problem; the instance carries no data.
    solver = Exact()
    # a suspect is 1 when guilty
    for name in SUSPECTS:
        solver.addVariable(name, 0, 1)

    # the getaway car held two, so at most two are guilty
    solver.addConstraint([(1, name) for name in SUSPECTS], False, 0, True, 2)

    # A suspect is guilty exactly when what he said is false.
    # Artie: "It wasn't me." and Crackitt: "No I wasn't." Each is guilty exactly when
    # he says something false about himself, which holds for either value, so
    # neither statement restricts anything.
    # Bill: "Crackitt was in it up to his neck." Bill is guilty exactly when Crackitt is not.
    solver.addConstraint([(1, "bill"), (1, "crackitt")], True, 1, True, 1)
    # Dodgy: "If Crackitt did it, Bill did it with him." False exactly when Crackitt
    # is guilty and Bill is not, and then Dodgy is guilty: dodgy = crackitt and not bill.
    solver.addConstraint([(1, "dodgy"), (-1, "crackitt")], False, 0, True, 0)
    solver.addConstraint([(1, "dodgy"), (1, "bill")], False, 0, True, 1)
    solver.addConstraint([(1, "dodgy"), (-1, "crackitt"), (1, "bill")], True, 0)
    # Edgy: "Nobody did it alone." False exactly when at most one suspect is guilty,
    # so edgy is guilty exactly when the number of guilty suspects is at most one.
    solver.addReification("edgy", True, [(-1, name) for name in SUSPECTS], -1)
    # Fingers: "That's right: it was Artie and Dodgy together." False exactly when
    # Artie and Dodgy are not both guilty: fingers = not (artie and dodgy).
    solver.addConstraint([(1, "fingers"), (1, "artie")], True, 1)
    solver.addConstraint([(1, "fingers"), (1, "dodgy")], True, 1)
    solver.addConstraint([(1, "fingers"), (1, "artie"), (1, "dodgy")], False, 0, True, 2)

    return solver, {name: name for name in SUSPECTS}
