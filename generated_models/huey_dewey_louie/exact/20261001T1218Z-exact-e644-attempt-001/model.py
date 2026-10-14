# Huey, Dewey and Louie: three nephews each make a statement and none of them lies. Decide who is
# guilty (1) and who is not (0).
from exact import Exact


def build(instance):
    # This problem has no instance data. The three statements belong to the problem statement.
    solver = Exact()
    for name in ("huey", "dewey", "louie"):
        solver.addVariable(name, 0, 1)  # 1 = guilty

    # Huey: "Dewey and Louie have an equal share in it; if one is guilty, so is the other."
    solver.addConstraint([(1, "dewey"), (-1, "louie")], True, 0, True, 0)
    # Dewey: "If Huey is guilty, then so am I."   huey -> dewey
    solver.addConstraint([(1, "dewey"), (-1, "huey")], True, 0)
    # Louie: "Dewey and I are not both guilty."
    solver.addConstraint([(1, "dewey"), (1, "louie")], False, 0, True, 1)

    return solver, {"huey": "huey", "dewey": "dewey", "louie": "louie"}
