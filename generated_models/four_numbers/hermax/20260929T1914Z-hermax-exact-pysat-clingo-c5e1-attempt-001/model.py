# Four numbers: given up to four distinct integers between 1 and 10, find three
# integers between 1 and 10 such that every given number is the sum of some
# subset of the three.
from itertools import product

from hermax.model import Model


def build(instance):
    numbers = instance["numbers"]
    n = 3  # how many integers are to be found

    m = Model()
    # x[j] = the j-th of the three integers
    x = m.int_vector("x", n, 1, 10)

    # Every given number is the sum of a subset of the three integers. For each given
    # number, list the triples of values for which some subset adds up to it, and
    # require x to be one of those triples.
    for target in numbers:
        allowed = [triple for triple in product(range(1, 11), repeat=n)
                   if any(sum(v for v, used in zip(triple, mask) if used) == target
                          for mask in product((0, 1), repeat=n))]
        m &= m.vector([x[j] for j in range(n)]).is_in(allowed)

    return m, {"x": x}
