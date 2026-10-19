# Periodic binary autocorrelation (CSPLib 005): choose a sequence of n bits, each +1 or -1,
# that minimises E = sum_{k=1}^{n-1} C_k^2, where C_k = sum_{i=0}^{n-1} S_i * S_{(i+k) mod n}.
import mip


def build(instance):
    # n is the sequence length, read from the instance.
    n = instance["n"]
    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # the sequence: bit S_i is +1 or -1. Encoded as S_i = 2*x_i - 1 with binary x_i
    # (x_i = 1 means S_i = +1, x_i = 0 means S_i = -1).
    x = [model.add_var(f"x_{i}", var_type=mip.BINARY) for i in range(n)]
    S = [2 * x[i] - 1 for i in range(n)]

    # product of two bits: w = x_i * x_j, linearised with three rows.
    # Then S_i * S_j = (2x_i - 1)(2x_j - 1) = 4*w - 2*x_i - 2*x_j + 1.
    products = {}

    def product(i, j):
        key = (min(i, j), max(i, j))
        if key not in products:
            w = model.add_var(f"w_{key[0]}_{key[1]}", var_type=mip.BINARY)
            model.add_constr(w <= x[key[0]])
            model.add_constr(w <= x[key[1]])
            model.add_constr(w >= x[key[0]] + x[key[1]] - 1)
            products[key] = w
        return products[key]

    # periodic autocorrelation C_k: the sum over i of S_i * S_{(i+k) mod n}.
    # Each C_k is a sum of n terms of +1 or -1, so it takes the values -n, -n+2, ..., n.
    energy = []
    for k in range(1, n):
        terms = []
        for i in range(n):
            j = (i + k) % n
            w = product(i, j)
            terms.append(4 * w - 2 * x[i] - 2 * x[j] + 1)
        c_k = mip.xsum(terms)

        # C_k squared, exact and linear: a one-hot choice of the value of C_k.
        # The square is taken from that value, so the objective is linear in the choice.
        values = list(range(-n, n + 1, 2))
        pick = {}
        for idx, v in enumerate(values):
            pick[v] = model.add_var(f"pick_{k}_{idx}", var_type=mip.BINARY)
        # exactly one value is chosen for C_k
        model += mip.xsum(pick.values()) == 1
        # the chosen value is the autocorrelation C_k of the sequence
        model += c_k == mip.xsum(v * pick[v] for v in values)
        # C_k^2 is the chosen value squared
        energy.append(mip.xsum(v * v * pick[v] for v in values))

    # minimise the sum of the squared autocorrelations, E = sum_k C_k^2
    model.objective = mip.xsum(energy)

    # the declared output: the bits S_0..S_{n-1}, each as an expression equal to -1 or +1
    return model, {"sequence": S}
