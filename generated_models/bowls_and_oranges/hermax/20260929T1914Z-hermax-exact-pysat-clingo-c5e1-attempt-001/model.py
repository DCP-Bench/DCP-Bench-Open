# Bowls and oranges: put oranges in bowls placed in a line, at most one per bowl,
# so that no three oranges are at equal distances from each other.
from hermax.model import Model


def build(instance):
    bowls = instance["n"]
    oranges = instance["m"]

    m = Model()
    # x[i] = the bowl, 1 to n, of the i-th orange, oranges in ascending order
    x = m.int_vector("x", oranges, 1, bowls)
    for i in range(oranges - 1):
        m &= (x[i] < x[i + 1])

    # occupied[p - 1] is true when bowl p holds an orange
    occupied = m.bool_vector("occupied", bowls)
    for i in range(oranges):
        for p in range(1, bowls + 1):
            m &= (x[i] == p).implies(occupied[p - 1])

    # No three oranges A, B, C with B in the middle: bowls p, p + d and p + 2d are
    # never all occupied.
    for p in range(1, bowls + 1):
        for d in range(1, (bowls - p) // 2 + 1):
            m &= (~occupied[p - 1] | ~occupied[p + d - 1] | ~occupied[p + 2 * d - 1])

    return m, {"x": x}
