# Langford's problem: arrange two copies of each of the numbers 1..k in a
# sequence of length 2k so that the two copies of i have exactly i numbers
# between them (they sit i + 1 places apart).
from hermax.model import Model


def build(instance):
    k = instance["k"]
    length = 2 * k  # two copies of every number 1..k

    m = Model()
    # sol[q] = the number placed at position q of the sequence
    sol = m.int_vector("sol", length, 1, k)

    # first[i][p] = the first copy of number i sits at position p, which puts
    # the second copy at position p + i + 1. Both copies must fit in the
    # sequence, so p ranges over 0 .. 2k - i - 2.
    first = {i: m.bool_vector(f"first_{i}", length - i - 1) for i in range(1, k + 1)}

    # each number has exactly one place for its first copy
    for i in range(1, k + 1):
        m &= first[i].exactly_one()

    # Each position of the sequence holds exactly one copy: either the first copy
    # of some number or the second copy of some number. (Stating "at most one"
    # would be enough, since 2k copies fill 2k positions; "exactly one" is the
    # statement of the problem.)
    for q in range(length):
        copies_here = []
        for i in range(1, k + 1):
            if q <= length - i - 2:  # a first copy of i may start at q
                copies_here.append(first[i][q])
            if q - i - 1 >= 0:  # a second copy of i may end at q
                copies_here.append(first[i][q - i - 1])
        m &= (sum(copies_here) == 1)

    # The sequence shows the number at both of its positions. This ties the
    # integer output sol to the placement above.
    for i in range(1, k + 1):
        for p in range(length - i - 1):
            m &= (~first[i][p] | (sol[p] == i))
            m &= (~first[i][p] | (sol[p + i + 1] == i))

    return m, {"sol": sol}
