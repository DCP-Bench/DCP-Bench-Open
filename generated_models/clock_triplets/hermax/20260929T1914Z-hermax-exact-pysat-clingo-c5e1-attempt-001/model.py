# Clock triplets: arrange the numbers 1 to 12 on a clock face so that no three
# neighbouring numbers add up to more than 21.
from hermax.model import Model


def build(instance):
    # The puzzle is fixed by the problem; the instance carries no data.
    n = 12
    m = Model()
    # x[i] = the number at position i of the clock
    x = m.int_vector("x", n, 1, n)

    # every number appears once
    m &= m.vector([x[i] for i in range(n)]).all_different()

    # no three neighbouring positions (going round the clock) add up to more than 21
    for i in range(n):
        m &= (x[i] + x[(i + 1) % n] + x[(i + 2) % n] <= 21)

    return m, {"x": x}
