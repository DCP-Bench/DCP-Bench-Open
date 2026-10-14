# Ages of the sons: three sons whose ages multiply to 36; knowing only their
# sum is not enough, so there is another triple with the same sum, and the
# oldest son is unique (the "blue eyes" clue).
from itertools import product

from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def build(instance):
    # The puzzle is fixed by the problem; the instance carries no data.
    pool = IDPool()
    # the ages of the sons, oldest first, and of the other triple with the same sum
    ages = [Integer(f"A{k}", 0, 36, vpool=pool) for k in (1, 2, 3)]
    other = [Integer(f"B{k}", 0, 36, vpool=pool) for k in (1, 2, 3)]
    engine = IntegerEngine(vars=ages + other, vpool=pool)

    # the other triple has the same sum
    engine.add_linear(ages[0] + ages[1] + ages[2] == other[0] + other[1] + other[2])
    cnf = engine.clausify()

    # The actual triple has a strictly oldest son (A1 > A2 >= A3), the other one may
    # have twins first (B1 >= B2 >= B3); both have the product 36. Forbid every
    # triple of values that is not of that kind.
    for triple in product(range(37), repeat=3):
        in_product = triple[0] * triple[1] * triple[2] == 36
        if not (in_product and triple[0] > triple[1] >= triple[2]):
            cnf.append([-ages[k].equals(triple[k]) for k in range(3)])
        if not (in_product and triple[0] >= triple[1] >= triple[2]):
            cnf.append([-other[k].equals(triple[k]) for k in range(3)])

    # the other triple has a different oldest son
    for value in range(37):
        cnf.append([-ages[0].equals(value), -other[0].equals(value)])

    return cnf, {"A1": ages[0], "A2": ages[1], "A3": ages[2]}
