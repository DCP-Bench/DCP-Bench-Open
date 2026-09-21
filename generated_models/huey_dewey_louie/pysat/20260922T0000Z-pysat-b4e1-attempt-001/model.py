# Three truthful cub scouts, and who among them is guilty.
# The statements are the puzzle, so the instance carries no fields.
from dcp_sat import Sat


def build(instance):
    sat = Sat()
    huey, dewey, louie = sat.bools(3)

    # Huey: Dewey and Louie are guilty together or not at all.
    sat.iff(dewey, louie)
    # Dewey: if Huey is guilty, so am I.
    sat.implies(huey, dewey)
    # Louie: Dewey and I are not both guilty.
    sat.at_most([dewey, louie], 1)
    return sat, {"huey": huey, "dewey": dewey, "louie": louie}
