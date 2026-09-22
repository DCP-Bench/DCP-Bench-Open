# Three truthful cub scouts, and who among them is guilty.
# The statements are the puzzle, so the instance carries no fields.
from pysat.formula import CNF, IDPool


def build(instance):
    pool = IDPool()
    huey = pool.id("huey")
    dewey = pool.id("dewey")
    louie = pool.id("louie")

    cnf = CNF()
    # Huey: Dewey and Louie are guilty together or not at all.
    cnf.append([-dewey, louie])
    cnf.append([dewey, -louie])
    # Dewey: if Huey is guilty, so am I.
    cnf.append([-huey, dewey])
    # Louie: Dewey and I are not both guilty.
    cnf.append([-dewey, -louie])
    return cnf, {"huey": huey, "dewey": dewey, "louie": louie}
