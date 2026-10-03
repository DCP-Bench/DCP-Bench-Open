"""Low autocorrelation binary sequence: a sequence of n bits, each +1 or -1, whose periodic
autocorrelations are as small as possible.

The k-th periodic autocorrelation is C_k = sum over i of S_i * S_((i + k) mod n), and the
energy to minimize is E = the sum of C_k squared for k = 1 .. n - 1.
"""
from docplex.mp.model import Model


def build(instance):
    n = instance["n"]  # length of the sequence

    model = Model("autocorrelation")

    # bit[i] is 1 when S_i is +1 and 0 when S_i is -1.
    bit = [model.binary_var(name=f"bit_{i}") for i in range(n)]

    # differ[i, j] is 1 when S_i and S_j have opposite signs, for i < j: it is the
    # exclusive or of the two bits, stated exactly with four rows.
    differ = {}
    for i in range(n):
        for j in range(i + 1, n):
            d = model.binary_var(name=f"differ_{i}_{j}")
            model.add_constraint(d >= bit[i] - bit[j])
            model.add_constraint(d >= bit[j] - bit[i])
            model.add_constraint(d <= bit[i] + bit[j])
            model.add_constraint(d <= 2 - bit[i] - bit[j])
            differ[i, j] = d

    # The k-th autocorrelation is a sum of n terms S_i * S_((i + k) mod n), each +1 when the two
    # signs agree and -1 when they differ. With `opposite` of them differing, C_k = n - 2 * opposite.
    # E needs the square of C_k, which is not linear, so `opposite` is picked from the values
    # 0..n through a one-hot variable, and the square (n - 2 * value) ** 2 is a constant of
    # each value.
    energy_terms = []
    for k in range(1, n):
        opposite = model.sum(differ[min(i, (i + k) % n), max(i, (i + k) % n)] for i in range(n))
        pick = [model.binary_var(name=f"pick_{k}_{v}") for v in range(n + 1)]
        model.add_constraint(model.sum(pick) == 1)
        model.add_constraint(opposite == model.sum(v * pick[v] for v in range(n + 1)))
        energy_terms.append(model.sum((n - 2 * v) ** 2 * pick[v] for v in range(n + 1)))

    # Objective: minimize the energy, the sum of the squared autocorrelations.
    model.minimize(model.sum(energy_terms))

    # The declared output: the sequence, +1 or -1 at each place.
    return model, {"sequence": [2 * bit[i] - 1 for i in range(n)]}
