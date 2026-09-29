# Averbach's card-passing riddle: three players X, Y, Z of three different
# nationalities (American, English, French) sit round a table, each passing
# three cards to the person on their right. Y passed to the American, and X
# passed to the person who passed to the Frenchwoman. Find who is who.
# A seat is 0, 1 or 2 and seat b+1 (mod 3) is to the right of seat b.
from exact import Exact


def build(instance):
    # The riddle fixes everything; the instance carries no data.
    solver = Exact()
    players = ["x", "y", "z"]
    nationalities = ["american", "english", "french"]
    for name in players + nationalities:
        solver.addVariable(name, 0, 2)

    # is_[name][seat] is 1 exactly when that person or nationality sits in seat
    # `seat`; each group of three takes all three seats, one each
    is_ = {}
    for name in players + nationalities:
        is_[name] = [f"{name}_in_{seat}" for seat in range(3)]
        for flag in is_[name]:
            solver.addVariable(flag, 0, 1)
        solver.addConstraint([(1, flag) for flag in is_[name]], True, 1, True, 1)
        solver.addConstraint([(seat, is_[name][seat]) for seat in range(3)] + [(-1, name)], True, 0, True, 0)
    for group in (players, nationalities):
        for seat in range(3):
            solver.addConstraint([(1, is_[name][seat]) for name in group], True, 1, True, 1)

    def right_to(a, b):
        """The seat a is immediately to the right of the seat b (mod 3):
        a - b = 1, or a - b = -2 when b is the last seat."""
        wrapped = f"{a}_right_of_{b}_wraps"
        solver.addVariable(wrapped, 0, 1)
        solver.addConstraint([(1, a), (-1, b), (3, wrapped)], True, 1, True, 1)

    # the American sits to the right of Y, since Y passed to the American
    right_to("american", "y")
    # X sits to the right of the Frenchwoman, since X passed to the person who passed to her
    right_to("x", "french")

    return solver, {name: name for name in players + nationalities}
