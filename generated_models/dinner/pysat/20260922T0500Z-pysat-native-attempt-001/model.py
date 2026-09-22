# Twenty people at dinner for twenty dollars.
# The prices and party sizes are the puzzle, so the instance carries no fields.
from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def build(instance):
    pool = IDPool()
    grandparents = Integer("grandparents", 1, 6, vpool=pool)
    parents = Integer("parents", 1, 10, vpool=pool)
    children = Integer("children", 1, 40, vpool=pool)

    engine = IntegerEngine(vars=[grandparents, parents, children], vpool=pool)
    # $3, $2 and $0.50 a head, doubled to clear the half dollar.
    engine.add_linear(6 * grandparents + 4 * parents + children == 40)
    engine.add_linear(grandparents + parents + children == 20)
    return engine.clausify(), {"grandparents": grandparents, "parents": parents,
                               "children": children}
