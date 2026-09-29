# Five floors: Baker, Cooper, Fletcher, Miller and Smith live on different floors
# of a five-floor house; the clues rule out some floors and some neighbours.
from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def build(instance):
    # The puzzle is fixed by the problem; the instance carries no data.
    pool = IDPool()
    # floor[name] = the floor, 1 to 5, where that person lives; the letters are the
    # initials of Baker, Cooper, Fletcher, Miller and Smith
    floor = {name: Integer(name, 1, 5, vpool=pool) for name in "BCFMS"}
    B, C, F, M, S = (floor[name] for name in "BCFMS")
    engine = IntegerEngine(vars=list(floor.values()), vpool=pool)

    # they all live on different floors
    engine.add_alldifferent(list(floor.values()))
    cnf = engine.clausify()

    # Baker does not live on the fifth floor
    cnf.append([-B.equals(5)])
    # Cooper does not live on the first floor
    cnf.append([-C.equals(1)])
    # Fletcher lives neither on the fifth nor on the first floor
    cnf.append([-F.equals(5)])
    cnf.append([-F.equals(1)])
    # Miller lives on a higher floor than Cooper: no pair with Miller on or below Cooper
    for c in range(1, 6):
        for mi in range(1, c + 1):
            cnf.append([-C.equals(c), -M.equals(mi)])

    def not_adjacent(p, q):
        # p and q do not live on neighbouring floors
        for v in range(1, 5):
            cnf.append([-p.equals(v), -q.equals(v + 1)])
            cnf.append([-q.equals(v), -p.equals(v + 1)])

    # Smith does not live on a floor adjacent to Fletcher's, and Fletcher not adjacent to Cooper's
    not_adjacent(S, F)
    not_adjacent(F, C)

    return cnf, floor
