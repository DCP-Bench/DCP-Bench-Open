# Huey, Dewey and Louie: the uncle questions three cub scouts who cannot tell a lie.
# Decide which of them (if any) are guilty. Each statement is true, and each
# person is a Boolean: guilty or not.
import cvc5.pythonic as cz


def build(instance):
    huey, dewey, louie = cz.Bools("huey dewey louie")

    constraints = []
    # Huey: Dewey and Louie have equal share in it; if one is guilty, so is the other.
    constraints.append(dewey == louie)
    # Dewey: If Huey is guilty, then so am I.
    constraints.append(cz.Implies(huey, dewey))
    # Louie: Dewey and I are not both guilty.
    constraints.append(cz.Not(cz.And(dewey, louie)))

    outputs = {"huey": huey, "dewey": dewey, "louie": louie}
    return constraints, outputs
