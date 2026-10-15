# Huey, Dewey and Louie: decide which of them are guilty, given that none of them can tell a lie.
from pyscipopt import Model


def build(instance):
    m = Model()
    # 1 if the cub scout is guilty, 0 if not
    huey = m.addVar(name="huey", vtype="B")
    dewey = m.addVar(name="dewey", vtype="B")
    louie = m.addVar(name="louie", vtype="B")

    # Huey's statement is true: Dewey and Louie have equal share, so one is guilty
    # exactly when the other is
    m.addCons(dewey - louie == 0)

    # Dewey's statement is true: if Huey is guilty, then so am I
    m.addCons(huey <= dewey)

    # Louie's statement is true: Dewey and I are not both guilty
    m.addCons(dewey + louie <= 1)

    return m, {"dewey": dewey, "huey": huey, "louie": louie}
