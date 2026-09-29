# Five floors: Baker, Cooper, Fletcher, Miller and Smith live on different floors
# of a five-floor house; the clues rule out some floors and some neighbours.
from hermax.model import Model


def build(instance):
    # The puzzle is fixed by the problem; the instance carries no data.
    m = Model()
    # floor[name] = the floor, 1 to 5, where that person lives; the letters are the
    # initials of Baker, Cooper, Fletcher, Miller and Smith
    floor = {name: m.int(name, 1, 5) for name in "BCFMS"}
    B, C, F, M, S = (floor[name] for name in "BCFMS")

    # they all live on different floors
    m &= m.vector(list(floor.values())).all_different()

    # Baker does not live on the fifth floor
    m &= (B != 5)
    # Cooper does not live on the first floor
    m &= (C != 1)
    # Fletcher lives neither on the fifth nor on the first floor
    m &= (F != 5)
    m &= (F != 1)
    # Miller lives on a higher floor than Cooper
    m &= (C < M)

    def not_adjacent(p, q):
        nonlocal m
        # p and q do not live on neighbouring floors
        for v in range(1, 5):
            m &= (~(p == v) | ~(q == v + 1))
            m &= (~(q == v) | ~(p == v + 1))

    # Smith does not live on a floor adjacent to Fletcher's, and Fletcher not adjacent to Cooper's
    not_adjacent(S, F)
    not_adjacent(F, C)

    return m, floor
