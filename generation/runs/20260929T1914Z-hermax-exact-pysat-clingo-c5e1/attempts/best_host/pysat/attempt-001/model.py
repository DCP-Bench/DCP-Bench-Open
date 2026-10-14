# Best host: seat six guests round a table so that everyone sits only next to
# guests they get along with.
from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine

# prefs[g] = the guests g is willing to sit next to; 0 Andrew, 1 Betty, 2 Cara,
# 3 Dave, 4 Erica, 5 Frank
PREFS = [[3, 5], [2, 4], [1, 5], [0, 4], [1, 3], [0, 2]]


def build(instance):
    # The puzzle is fixed by the problem; the instance carries no data.
    n = len(PREFS)
    pool = IDPool()
    # x[i] = the guest at seat i, going round the table
    x = [Integer(f"x_{i}", 0, n - 1, vpool=pool) for i in range(n)]
    engine = IntegerEngine(vars=x, vpool=pool)

    # every guest gets one seat
    engine.add_alldifferent(x)
    cnf = engine.clausify()

    # Two guests in neighbouring seats must each be willing to sit next to the other:
    # forbid every pair of neighbours that is not compatible.
    for i in range(n):
        j = (i + 1) % n
        for a in range(n):
            for b in range(n):
                if b not in PREFS[a] or a not in PREFS[b]:
                    cnf.append([-x[i].equals(a), -x[j].equals(b)])

    return cnf, {"x": x}
