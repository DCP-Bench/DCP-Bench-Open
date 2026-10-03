# Kidney exchange: people on a waiting list for a kidney transplant, with a directed
# graph saying who can donate to whom. Choose the transplants so that anyone who gives
# a kidney also receives one and nobody gives or receives more than one, with as many
# transplants as possible.
import functools
import operator

from hermax.model import Model


def build(instance):
    n = instance["num_people"]  # number of people on the waiting list
    # compatible[i] = the people (numbered from 1) that person i can donate to
    compatible = instance["compatible"]

    m = Model()
    # transplants[i][j] = person i donates a kidney to person j
    transplants = m.bool_matrix("transplants", n, n)

    # Compatibility: person i can only donate to the people in compatible[i].
    for i in range(n):
        for j in range(n):
            if j + 1 not in compatible[i]:
                m &= ~transplants[i][j]

    for i in range(n):
        # Anyone who gives a kidney must receive one: if row i has a transplant, so
        # has column i.
        receives = functools.reduce(operator.or_, [transplants[k][i] for k in range(n)])
        for j in range(n):
            m &= (~transplants[i][j] | receives)
        # Each person donates at most one kidney and receives at most one.
        m &= transplants.row(i).at_most_one()
        m &= transplants.col(i).at_most_one()

    # Maximise the number of transplants. A soft clause pays when its literal is false,
    # so every possible transplant that is not made pays 1 (the cells that compatibility
    # forbids are always empty and are left out).
    for i in range(n):
        for j in range(n):
            if j + 1 in compatible[i]:
                m.obj[1] += transplants[i][j]

    return m, {"transplants": transplants}
