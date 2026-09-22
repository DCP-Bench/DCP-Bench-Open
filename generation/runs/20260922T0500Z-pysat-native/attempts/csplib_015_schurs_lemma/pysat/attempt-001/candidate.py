# Put balls 1..n into c boxes so no triple x + y = z shares a box.
from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def build(instance):
    n = instance["n"]
    boxes = instance["c"]

    pool = IDPool()
    balls = [Integer(f"ball{i}", 1, boxes, vpool=pool) for i in range(n)]
    engine = IntegerEngine(vars=balls, vpool=pool)
    cnf = engine.clausify()
    for x in range(1, n):
        for y in range(1, n - x + 1):
            z = x + y
            if z <= n:
                # No box holds all three at once.
                for box in range(1, boxes + 1):
                    cnf.append([-balls[x - 1].equals(box),
                                -balls[y - 1].equals(box),
                                -balls[z - 1].equals(box)])
    return cnf, {"balls": balls}
