# Magic sequence: find x[0..n-1], each between 0 and n-1, such that for every
# i the number i occurs exactly x[i] times in the sequence.
from hermax.model import Model


def build(instance):
    n = instance["n"]  # length of the sequence

    m = Model()
    # x[i] = how many times the number i occurs in the sequence; the values
    # lie between 0 and n-1 as the problem statement fixes
    x = m.int_vector("x", n, 0, n - 1)

    # for every i, the number i occurs exactly x[i] times in the sequence
    for i in range(n):
        m &= (sum((x[j] == i) for j in range(n)) == x[i])

    return m, {"x": x}
