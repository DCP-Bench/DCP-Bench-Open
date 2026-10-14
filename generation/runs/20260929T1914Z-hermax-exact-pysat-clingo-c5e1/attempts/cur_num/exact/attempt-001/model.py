# Curious number: 48 has the peculiarity that adding 1 to it gives a square and
# adding 1 to its half gives a square. Find another number, from 1 to 10000, with it.
from exact import Exact


def build(instance):
    # The puzzle is fixed by the problem; the instance carries no data.
    limit = 10000  # the number and every number derived from it is between 1 and 10000
    solver = Exact()
    for name in ("peculiar", "plus_one", "half", "half_plus_one"):
        solver.addVariable(name, 1, limit)
    # the square roots of the two squares, at most 100 since the squares are at most 10000
    solver.addVariable("root_of_number", 1, 100)
    solver.addVariable("root_of_half", 1, 100)

    # if you add 1 to it the result is a square number
    solver.addConstraint([(1, "plus_one"), (-1, "peculiar")], True, 1, True, 1)
    solver.addMultiplication(["root_of_number", "root_of_number"], True, "plus_one", True, "plus_one")
    # if you add 1 to its half you also get a square number
    solver.addConstraint([(1, "peculiar"), (-2, "half")], True, 0, True, 0)
    solver.addConstraint([(1, "half_plus_one"), (-1, "half")], True, 1, True, 1)
    solver.addMultiplication(["root_of_half", "root_of_half"], True, "half_plus_one", True, "half_plus_one")

    # 48 is already known: peculiar is above 48 or below it
    solver.addVariable("above", 0, 1)
    solver.addVariable("below", 0, 1)
    solver.addReification("above", True, [(1, "peculiar")], 49)
    solver.addReification("below", True, [(-1, "peculiar")], -47)
    solver.addConstraint([(1, "above"), (1, "below")], True, 1)

    return solver, {"peculiar": "peculiar"}
