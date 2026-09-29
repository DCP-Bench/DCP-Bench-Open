# Hanging weights: thirteen weights A-M, each an integer from 1 to 13 and all
# different, hang from a system of bars that has to balance.
from exact import Exact


def build(instance):
    # The puzzle is fixed by the problem; the instance carries no data.
    names = list("abcdefghijklm")

    solver = Exact()
    for name in names:
        solver.addVariable(name, 1, 13)

    # the weights are all different: indicators say which value a weight has, and
    # each value is used by at most one weight
    is_ = {name: {v: f"{name}_is_{v}" for v in range(1, 14)} for name in names}
    for name in names:
        for v in range(1, 14):
            solver.addVariable(is_[name][v], 0, 1)
        solver.addConstraint([(1, is_[name][v]) for v in range(1, 14)], True, 1, True, 1)
        solver.addConstraint([(v, is_[name][v]) for v in range(1, 14)] + [(-1, name)], True, 0, True, 0)
    for v in range(1, 14):
        solver.addConstraint([(1, is_[name][v]) for name in names], False, 0, True, 1)

    # Every bar balances: the weights on either side of the pivot, each times its
    # distance from the pivot, are equal, and a bar hanging beneath another counts as
    # one weight equal to its total. The bottom right bar has 5*C = D and the bar
    # above it 3*G = 2*(C+D). Each line is left side minus right side = 0.
    balances = [
        [(4, "a"), (-1, "b")],
        [(5, "c"), (-1, "d")],
        [(3, "e"), (-2, "f")],
        [(3, "g"), (-2, "c"), (-2, "d")],
        [(3, "a"), (3, "b"), (2, "j"), (-1, "k"), (-2, "g"), (-2, "c"), (-2, "d")],
        [(3, "h"), (-2, "e"), (-2, "f"), (-3, "i")],
        [(1, "h"), (1, "i"), (1, "e"), (1, "f"), (-1, "l"), (-4, "m")],
        [(4, "l"), (4, "m"), (4, "h"), (4, "i"), (4, "e"), (4, "f"),
         (-3, "j"), (-3, "k"), (-3, "g"), (-3, "a"), (-3, "b"), (-3, "c"), (-3, "d")],
    ]
    for terms in balances:
        solver.addConstraint(terms, True, 0, True, 0)

    return solver, {name: name for name in names}
