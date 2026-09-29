# Ages of the sons: three sons whose ages multiply to 36; knowing only their
# sum is not enough, so there is another triple with the same sum, and the
# oldest son is unique (the "blue eyes" clue).
from itertools import product

from hermax.model import Model


def build(instance):
    # The puzzle is fixed by the problem; the instance carries no data.
    m = Model()
    # the ages of the sons, oldest first, and of the other triple with the same sum
    ages = [m.int(f"A{k}", 0, 36) for k in (1, 2, 3)]
    other = [m.int(f"B{k}", 0, 36) for k in (1, 2, 3)]

    # Triples of ages, in decreasing order, whose product is 36. The actual triple has
    # a strictly oldest son (A1 > A2 >= A3), the other one may have twins first.
    products = [t for t in product(range(37), repeat=3) if t[0] * t[1] * t[2] == 36]
    m &= m.vector(ages).is_in([t for t in products if t[0] > t[1] >= t[2]])
    m &= m.vector(other).is_in([t for t in products if t[0] >= t[1] >= t[2]])

    # the other triple has the same sum, and a different oldest son
    m &= (ages[0] + ages[1] + ages[2] == other[0] + other[1] + other[2])
    m &= (ages[0] != other[0])

    return m, {"A1": ages[0], "A2": ages[1], "A3": ages[2]}
