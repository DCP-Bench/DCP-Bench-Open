# Bowls and oranges: put oranges in bowls placed in a line, at most one per bowl,
# so that no three oranges are at equal distances from each other.
from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def build(instance):
    bowls = instance["n"]
    oranges = instance["m"]

    pool = IDPool()
    # x[i] = the bowl, 1 to n, of the i-th orange, oranges in ascending order
    x = [Integer(f"x_{i}", 1, bowls, vpool=pool) for i in range(oranges)]
    engine = IntegerEngine(vars=x, vpool=pool)
    cnf = engine.clausify()

    # ascending order: the next orange is in a later bowl
    for i in range(oranges - 1):
        for p in range(1, bowls + 1):
            for q in range(1, p + 1):
                cnf.append([-x[i].equals(p), -x[i + 1].equals(q)])

    # occupied[p] is true when bowl p holds an orange
    occupied = {p: pool.id(("occupied", p)) for p in range(1, bowls + 1)}
    for i in range(oranges):
        for p in range(1, bowls + 1):
            cnf.append([-x[i].equals(p), occupied[p]])

    # No three oranges A, B, C with B in the middle: bowls p, p + d and p + 2d are
    # never all occupied.
    for p in range(1, bowls + 1):
        for d in range(1, (bowls - p) // 2 + 1):
            cnf.append([-occupied[p], -occupied[p + d], -occupied[p + 2 * d]])

    return cnf, {"x": x}
