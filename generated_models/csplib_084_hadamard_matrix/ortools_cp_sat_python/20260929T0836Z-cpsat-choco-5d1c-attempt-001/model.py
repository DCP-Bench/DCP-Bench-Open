# Hadamard matrix (Legendre pairs): for an odd l with m = (l - 1) / 2, find two
# sequences a and b of length l with entries +1 or -1, each summing to 1, whose
# periodic autocorrelations satisfy PAF(a, s) + PAF(b, s) = -2 for s = 1..m.
from ortools.sat.python import cp_model


def build(instance):
    l = instance["l"]  # length of the sequences (odd)
    m = (l - 1) // 2

    model = cp_model.CpModel()

    def sequence(name):
        """A sequence of l values, each -1 or +1, with the Booleans that say which."""
        plus = [model.new_bool_var(f"{name}_plus_{i}") for i in range(l)]
        values = [
            model.new_int_var_from_domain(cp_model.Domain.from_values([-1, 1]), f"{name}_{i}") for i in range(l)
        ]
        for i in range(l):
            model.add(values[i] == 2 * plus[i] - 1)
        return plus, values

    plus_a, a = sequence("a")
    plus_b, b = sequence("b")

    # each sequence sums to 1
    model.add(sum(a) == 1)
    model.add(sum(b) == 1)

    def paf(name, plus, s):
        """Periodic autocorrelation sum_i x_i * x_((i+s) mod l) of a +-1 sequence, as a linear expression."""
        agree = []
        for i in range(l):
            same = model.new_bool_var(f"{name}_same_{s}_{i}")
            model.add(plus[i] == plus[(i + s) % l]).only_enforce_if(same)
            model.add(plus[i] != plus[(i + s) % l]).only_enforce_if(same.negated())
            agree.append(same)
        # each agreeing pair contributes +1 and each disagreeing pair -1
        return 2 * sum(agree) - l

    # the autocorrelations of a and b cancel out: PAF(a, s) + PAF(b, s) = -2
    for s in range(1, m + 1):
        model.add(paf("a", plus_a, s) + paf("b", plus_b, s) == -2)

    return model, {"a": a, "b": b}
