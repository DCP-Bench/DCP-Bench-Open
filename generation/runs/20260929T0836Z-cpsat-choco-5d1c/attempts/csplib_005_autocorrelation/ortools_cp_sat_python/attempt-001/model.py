# Low autocorrelation binary sequences: choose a sequence of n values, each +1
# or -1, that minimises the sum of the squared periodic autocorrelations
# C_k = sum_i S_i * S_((i+k) mod n) for k = 1..n-1.
from ortools.sat.python import cp_model


def build(instance):
    n = instance["n"]  # length of the sequence

    model = cp_model.CpModel()

    # plus[i] is true when S_i = +1 and false when S_i = -1
    plus = [model.new_bool_var(f"plus_{i}") for i in range(n)]
    # sequence[i] = S_i, either -1 or +1 (never 0)
    sequence = [model.new_int_var_from_domain(cp_model.Domain.from_values([-1, 1]), f"sequence_{i}") for i in range(n)]
    for i in range(n):
        model.add(sequence[i] == 2 * plus[i] - 1)

    # same[(i, j)] is true when S_i == S_j, so S_i * S_j = 2 * same - 1
    same = {}

    def product(i, j):
        """S_i * S_j as a linear expression."""
        key = (min(i, j), max(i, j))
        if key not in same:
            lit = model.new_bool_var(f"same_{key[0]}_{key[1]}")
            model.add(plus[key[0]] == plus[key[1]]).only_enforce_if(lit)
            model.add(plus[key[0]] != plus[key[1]]).only_enforce_if(lit.negated())
            same[key] = lit
        return 2 * same[key] - 1

    # energy E = sum of the squares of the periodic autocorrelations C_1 .. C_{n-1}
    squares = []
    for k in range(1, n):
        correlation = model.new_int_var(-n, n, f"C_{k}")
        model.add(correlation == sum(product(i, (i + k) % n) for i in range(n)))
        square = model.new_int_var(0, n * n, f"C_{k}_squared")
        model.add_multiplication_equality(square, [correlation, correlation])
        squares.append(square)
    energy = model.new_int_var(0, (n - 1) * n * n, "energy")
    model.add(energy == sum(squares))
    model.minimize(energy)

    return model, {"sequence": sequence}
