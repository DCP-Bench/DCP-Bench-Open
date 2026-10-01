# Low autocorrelation binary sequences: choose a sequence of n values, each +1
# or -1, that minimises the sum of the squared periodic autocorrelations
# C_k = sum_i S_i * S_((i+k) mod n) for k = 1..n-1.
import cpmpy as cp


def build(instance):
    n = instance["n"]  # length of the sequence

    # plus[i] is true when S_i = +1 and false when S_i = -1. Using a Boolean keeps the value
    # away from 0 without a "not equal to 0" constraint, and the products below become linear.
    plus = cp.boolvar(shape=n, name="plus")
    # sequence[i] = S_i, either -1 or +1.
    sequence = 2 * plus - 1

    model = cp.Model()

    # The k-th periodic autocorrelation C_k is the sum over i of S_i * S_((i+k) mod n).
    # Two entries multiply to +1 when equal and to -1 when different, i.e. 2 * [equal] - 1.
    correlation = cp.intvar(-n, n, shape=n - 1, name="correlation")  # correlation[k-1] = C_k
    for k in range(1, n):
        model += correlation[k - 1] == cp.sum([2 * (plus[i] == plus[(i + k) % n]) - 1 for i in range(n)])

    # Energy E = sum of the squares of C_1 .. C_(n-1), to be minimised.
    energy = cp.intvar(0, (n - 1) * n * n, name="energy")
    model += energy == cp.sum([c ** 2 for c in correlation])
    model.minimize(energy)

    return model, {"sequence": sequence}
