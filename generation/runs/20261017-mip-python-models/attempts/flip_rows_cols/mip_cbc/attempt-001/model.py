# Flip rows and columns of a matrix of positive and negative numbers so that every
# row and every column sums to a non-negative value, and the overall sum of the
# resulting matrix is minimal. Outputs row_signs and col_signs (each -1 or 1).
import itertools

import mip


def build(instance):
    a = instance["input_matrix"]
    nr = len(a)
    nc = len(a[0])

    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # p[i] = 1 means row i is flipped (sign -1).
    p = [model.add_var(f"p_{i}", var_type=mip.BINARY) for i in range(nr)]

    # One binary per column sign pattern: w[k] = 1 means the column signs are
    # patterns[k]. Exactly one pattern is chosen.
    patterns = list(itertools.product((1, -1), repeat=nc))
    w = [model.add_var(f"w_{k}", var_type=mip.BINARY) for k in range(len(patterns))]
    model.add_constr(mip.xsum(w) == 1)

    # For a chosen column pattern s, the unflipped row sums R[i] are fixed. A row
    # sum after flipping must be >= 0, so the row sign is forced where R[i] != 0.
    row_sums = []
    for s in patterns:
        row_sums.append([sum(s[j] * a[i][j] for j in range(nc)) for i in range(nr)])

    for k, s in enumerate(patterns):
        for i in range(nr):
            R = row_sums[k][i]
            # row i is positive without a flip: it must not be flipped when pattern k holds
            if R > 0:
                model.add_constr(p[i] <= 1 - w[k])
            # row i is negative without a flip: it must be flipped when pattern k holds
            elif R < 0:
                model.add_constr(p[i] >= w[k])

    # Column sums after flipping must be >= 0. With the column sign s_j fixed by the
    # pattern, the column sum is s_j * sum_i (1 - 2 p_i) a_ij. The big-M is the
    # largest possible violation, computed from the data.
    for k, s in enumerate(patterns):
        for j in range(nc):
            col_total = sum(a[i][j] for i in range(nr))
            big_m = sum(abs(a[i][j]) for i in range(nr))
            coef = {p[i]: -2 * s[j] * a[i][j] for i in range(nr)}
            coef[w[k]] = -big_m
            expr = mip.LinExpr(list(coef.keys()), list(coef.values()), s[j] * col_total)
            model.add_constr(expr >= -big_m)

    # The total sum of the flipped matrix. Each row's sum is forced to be >= 0, so
    # its flipped total equals |R[i]| for the chosen pattern.
    obj_coef = [sum(abs(row_sums[k][i]) for i in range(nr)) for k in range(len(patterns))]
    model.objective = mip.LinExpr(list(w), obj_coef, 0)

    row_signs = [1 - 2 * p[i] for i in range(nr)]
    col_signs = [
        mip.LinExpr(list(w), [patterns[k][j] for k in range(len(patterns))], 0)
        for j in range(nc)
    ]
    return model, {"row_signs": row_signs, "col_signs": col_signs}
