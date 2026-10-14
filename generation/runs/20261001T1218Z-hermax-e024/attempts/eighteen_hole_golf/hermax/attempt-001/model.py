# Eighteen-hole golf: lay out a course of 18 holes, each of length (par) 3, 4 or 5, with a
# total length of 72.
from hermax.model import Model


def build(instance):
    # The course size, hole lengths and total are fixed by the problem; the instance
    # carries no data.
    num_holes = 18
    total_length = 72
    shortest, longest = 3, 5

    m = Model()
    # holes[i] = the length of hole i, 3, 4 or 5
    holes = m.int_vector("holes", num_holes, shortest, longest)

    # the course has a total length of 72
    m &= (sum(holes[i] for i in range(num_holes)) == total_length)

    return m, {"holes": holes}
