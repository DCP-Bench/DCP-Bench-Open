# Ages of the sons: three sons whose ages multiply to 36; knowing only their
# sum is not enough, so there is another triple with the same sum, and the
# oldest son is unique (the "blue eyes" clue).
from exact import Exact


def build(instance):
    # The puzzle is fixed by the problem; the instance carries no data.
    solver = Exact()
    # the ages of the sons, oldest first, and of the other triple with the same sum
    ages = ["A1", "A2", "A3"]
    other = ["B1", "B2", "B3"]
    for name in ages + other:
        solver.addVariable(name, 0, 36)
    # a variable fixed to 36, the product of the ages
    solver.addVariable("thirty_six", 36, 36)

    # both triples have the product 36: (first * second) * third
    for prefix, names in (("A", ages), ("B", other)):
        pair = f"{prefix}_first_two"
        solver.addVariable(pair, 0, 36 * 36)
        solver.addMultiplication([names[0], names[1]], True, pair, True, pair)
        solver.addMultiplication([pair, names[2]], True, "thirty_six", True, "thirty_six")

    # the actual triple has a strictly oldest son (A1 > A2 >= A3), the other one may have twins first
    solver.addConstraint([(1, "A1"), (-1, "A2")], True, 1)
    solver.addConstraint([(1, "A2"), (-1, "A3")], True, 0)
    solver.addConstraint([(1, "B1"), (-1, "B2")], True, 0)
    solver.addConstraint([(1, "B2"), (-1, "B3")], True, 0)

    # the other triple has the same sum
    solver.addConstraint([(1, name) for name in ages] + [(-1, name) for name in other], True, 0, True, 0)

    # and a different oldest son: A1 > B1 or B1 > A1
    solver.addVariable("older", 0, 1)
    solver.addVariable("younger", 0, 1)
    solver.addReification("older", True, [(1, "A1"), (-1, "B1")], 1)
    solver.addReification("younger", True, [(1, "B1"), (-1, "A1")], 1)
    solver.addConstraint([(1, "older"), (1, "younger")], True, 1)

    return solver, {name: name for name in ages}
