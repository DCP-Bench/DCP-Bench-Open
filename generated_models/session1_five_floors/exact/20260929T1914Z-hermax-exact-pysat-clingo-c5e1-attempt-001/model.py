# Five floors: Baker, Cooper, Fletcher, Miller and Smith live on different floors
# of a five-floor house; the clues rule out some floors and some neighbours.
from exact import Exact


def build(instance):
    # The puzzle is fixed by the problem; the instance carries no data.
    names = "BCFMS"  # the initials of Baker, Cooper, Fletcher, Miller and Smith

    solver = Exact()
    # floor[name] = the floor, 1 to 5, where that person lives. The bounds already
    # carry some clues: Baker not on the fifth floor, Cooper not on the first,
    # Fletcher on neither the first nor the fifth.
    bounds = {"B": (1, 4), "C": (2, 5), "F": (2, 4), "M": (1, 5), "S": (1, 5)}
    for name in names:
        solver.addVariable(name, *bounds[name])

    # they all live on different floors: indicators say which floor a person has,
    # and each floor is used by at most one person
    is_ = {name: {v: f"{name}_on_{v}" for v in range(1, 6)} for name in names}
    for name in names:
        for v in range(1, 6):
            solver.addVariable(is_[name][v], 0, 1)
        solver.addConstraint([(1, is_[name][v]) for v in range(1, 6)], True, 1, True, 1)
        solver.addConstraint([(v, is_[name][v]) for v in range(1, 6)] + [(-1, name)], True, 0, True, 0)
    for v in range(1, 6):
        solver.addConstraint([(1, is_[name][v]) for name in names], False, 0, True, 1)

    # Miller lives on a higher floor than Cooper
    solver.addConstraint([(1, "M"), (-1, "C")], True, 1)

    def not_adjacent(p, q):
        # p and q do not live on neighbouring floors
        for v in range(1, 5):
            solver.addConstraint([(1, is_[p][v]), (1, is_[q][v + 1])], False, 0, True, 1)
            solver.addConstraint([(1, is_[q][v]), (1, is_[p][v + 1])], False, 0, True, 1)

    # Smith does not live on a floor adjacent to Fletcher's, and Fletcher not adjacent to Cooper's
    not_adjacent("S", "F")
    not_adjacent("F", "C")

    return solver, {name: name for name in names}
