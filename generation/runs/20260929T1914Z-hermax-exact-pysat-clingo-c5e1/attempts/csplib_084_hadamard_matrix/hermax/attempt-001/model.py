# Hadamard matrix (Legendre pairs): for an odd l with m = (l - 1) / 2, find two
# sequences a and b of length l with entries +1 or -1, each summing to 1, whose
# periodic autocorrelations satisfy PAF(a, s) + PAF(b, s) = -2 for s = 1..m.
from hermax.model import Model


def build(instance):
    l = instance["l"]  # length of the sequences (odd)
    half = (l - 1) // 2

    m = Model()

    def sequence(name):
        """plus[i] says whether entry i is +1; values[i] is the entry itself, -1 or +1."""
        nonlocal m
        plus = m.bool_vector(f"{name}_plus", l)
        values = m.int_vector(name, l, -1, 1)
        for i in range(l):
            m &= (~plus[i] | (values[i] == 1))
            m &= (plus[i] | (values[i] == -1))
        # the entries sum to 1: (l + 1) / 2 of them are +1
        m &= (sum(1 * plus[i] for i in range(l)) == (l + 1) // 2)
        return plus, values

    plus_a, a = sequence("a")
    plus_b, b = sequence("b")

    def agreements(name, plus, s):
        """Literals that say whether entries i and i + s (mod l) are equal."""
        nonlocal m
        agree = []
        for i in range(l):
            p, q = plus[i], plus[(i + s) % l]
            same = m.bool(f"{name}_same_{s}_{i}")
            m &= (~same | ~p | q)
            m &= (~same | p | ~q)
            m &= (same | p | q)
            m &= (same | ~p | ~q)
            agree.append(same)
        return agree

    # PAF(a, s) + PAF(b, s) = -2. Each PAF is 2 * (equal pairs) - l, so the
    # condition says that the equal pairs of a and b together number l - 1.
    for s in range(1, half + 1):
        same = agreements("a", plus_a, s) + agreements("b", plus_b, s)
        m &= (sum(1 * lit for lit in same) == l - 1)

    return m, {"a": a, "b": b}
