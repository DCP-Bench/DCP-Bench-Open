# 100 bushels among 100 people: 3 per man, 2 per woman, half per child,
# with five times as many women as men.
# The puzzle statement fixes every number, so the instance carries no fields.
from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def build(instance):
    pool = IDPool()
    # Five times as many women as men caps the men at 20 within 100 people,
    # which keeps the domain encodings small.
    men = Integer("men", 0, 20, vpool=pool)
    women = Integer("women", 0, 100, vpool=pool)
    children = Integer("children", 0, 100, vpool=pool)

    engine = IntegerEngine(vars=[men, women, children], vpool=pool)
    engine.add_linear(men + women + children == 100)
    # Doubled to clear the child's half bushel.
    engine.add_linear(6 * men + 4 * women + children == 200)
    engine.add_linear(5 * men - women == 0)
    return engine.clausify(), {"men": men, "women": women, "children": children}
