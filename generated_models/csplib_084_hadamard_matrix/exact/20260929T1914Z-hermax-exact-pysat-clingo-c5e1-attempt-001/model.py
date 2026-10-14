# Hadamard matrix (Legendre pairs): for an odd l with m = (l - 1) / 2, find two
# sequences a and b of length l with entries +1 or -1, each summing to 1, whose
# periodic autocorrelations satisfy PAF(a, s) + PAF(b, s) = -2 for s = 1..m.
from exact import Exact


def build(instance):
    l = instance["l"]  # length of the sequences (odd)
    half = (l - 1) // 2

    solver = Exact()

    def sequence(name):
        """plus[i] is 1 when entry i is +1; values[i] is the entry itself, -1 or +1."""
        plus = [f"{name}_plus_{i}" for i in range(l)]
        values = [f"{name}_{i}" for i in range(l)]
        for i in range(l):
            solver.addVariable(plus[i], 0, 1)
            solver.addVariable(values[i], -1, 1)
            # the entry is 2 * plus - 1, so never 0
            solver.addConstraint([(1, values[i]), (-2, plus[i])], True, -1, True, -1)
        # the entries sum to 1: (l + 1) / 2 of them are +1
        solver.addConstraint([(1, name_) for name_ in plus], True, (l + 1) // 2, True, (l + 1) // 2)
        return plus, values

    plus_a, a = sequence("a")
    plus_b, b = sequence("b")

    def agreements(name, plus, s):
        """0/1 variables that say whether entries i and i + s (mod l) are equal."""
        agree = []
        for i in range(l):
            p, q = plus[i], plus[(i + s) % l]
            same = f"{name}_same_{s}_{i}"
            solver.addVariable(same, 0, 1)
            solver.addConstraint([(1, same), (1, p), (1, q)], True, 1)  # both 0: equal
            solver.addConstraint([(1, same), (-1, p), (-1, q)], True, -1)  # both 1: equal
            solver.addConstraint([(1, same), (1, p), (-1, q)], False, 0, True, 1)  # p = 1, q = 0: not equal
            solver.addConstraint([(1, same), (-1, p), (1, q)], False, 0, True, 1)  # p = 0, q = 1: not equal
            agree.append(same)
        return agree

    # PAF(a, s) + PAF(b, s) = -2. Each PAF is 2 * (equal pairs) - l, so the
    # condition says that the equal pairs of a and b together number l - 1.
    for s in range(1, half + 1):
        same = agreements("a", plus_a, s) + agreements("b", plus_b, s)
        solver.addConstraint([(1, name) for name in same], True, l - 1, True, l - 1)

    return solver, {"a": a, "b": b}
