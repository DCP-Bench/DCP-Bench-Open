# Four numbers: given up to four distinct integers between 1 and 10, find three
# integers between 1 and 10 such that every given number is the sum of some
# subset of the three.
from itertools import product

from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def build(instance):
    numbers = instance["numbers"]
    n = 3  # how many integers are to be found

    pool = IDPool()
    # x[j] = the j-th of the three integers
    x = [Integer(f"x_{j}", 1, 10, vpool=pool) for j in range(n)]
    engine = IntegerEngine(vars=x, vpool=pool)
    cnf = engine.clausify()

    # Every given number is the sum of a subset of the three integers: forbid each
    # triple of values from which no subset adds up to a given number.
    for target in numbers:
        for triple in product(range(1, 11), repeat=n):
            reachable = any(sum(v for v, used in zip(triple, mask) if used) == target
                            for mask in product((0, 1), repeat=n))
            if not reachable:
                cnf.append([-x[j].equals(triple[j]) for j in range(n)])

    return cnf, {"x": x}
