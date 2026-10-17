# Flip the sign of entire rows and columns of an array of positive and negative
# numbers, so that every row and every column sums to positive numbers (or zero),
# and the overall sum of the flipped array is as small as possible.
# Outputs: row_signs and col_signs, each entry -1 or 1.
import itertools

import mip


def build(instance):
    a = instance["input_matrix"]  # the array, read from the instance
    nr = len(a)
    nc = len(a[0])

    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # p[i] = 1 if row i is flipped (row_signs[i] = -1), 0 otherwise.
    p = [model.add_var(f"p_{i}", var_type=mip.BINARY) for i in range(nr)]

    # Flip the columns as one sign pattern. There are 2^nc patterns for the nc columns;
    # w[k] = 1 if the column signs are patterns[k]. Exactly one pattern is chosen.
    # Encoding: an explicit product p[i] * q[j] of the row and column flips gave a weak
    # LP relaxation (CBC timed out on the example), so the column choice is one-hot here.
    patterns = list(itertools.product((1, -1), repeat=nc))
    w = [model.add_var(f"w_{k}", var_type=mip.BINARY) for k in range(len(patterns))]
    model.add_constr(mip.xsum(w) == 1)

    # The row sums of the array with the chosen column flips, before any row flip.
    row_sums = []
    for s in patterns:
        row_sums.append([sum(s[j] * a[i][j] for j in range(nc)) for i in range(nr)])

    # Every row sums to positive numbers (or zero) after flipping: when the column
    # pattern k is chosen, a row whose sum is positive must not be flipped, and a row
    # whose sum is negative must be flipped. Rows with a zero sum are free.
    for k in range(len(patterns)):
        for i in range(nr):
            R = row_sums[k][i]
            if R > 0:
                model.add_constr(p[i] <= 1 - w[k])
            elif R < 0:
                model.add_constr(p[i] >= w[k])

    # Every column sums to positive numbers (or zero) after flipping. With the column
    # pattern k chosen, the column sum is s_j * sum_i (1 - 2 p_i) a_ij. The big-M for
    # the constraint is the sum of the absolute values in column j of the instance data,
    # which bounds how far the column sum can fall below zero, so the constraint is
    # inactive when pattern k is not chosen.
    for k, s in enumerate(patterns):
        for j in range(nc):
            col_total = sum(a[i][j] for i in range(nr))
            big_m = sum(abs(a[i][j]) for i in range(nr))
            coef = {p[i]: -2 * s[j] * a[i][j] for i in range(nr)}
            coef[w[k]] = -big_m
            expr = mip.LinExpr(list(coef.keys()), list(coef.values()), s[j] * col_total)
            model.add_constr(expr >= -big_m)

    # The overall sum of the flipped array is minimised. The row constraints above force
    # each flipped row sum to equal the absolute value of its unflipped sum, so the
    # total for pattern k is the sum of those absolute values.
    obj_coef = [sum(abs(row_sums[k][i]) for i in range(nr)) for k in range(len(patterns))]
    model.objective = mip.LinExpr(list(w), obj_coef, 0)

    # Output: the sign of each row and column, -1 or 1.
    row_signs = [1 - 2 * p[i] for i in range(nr)]
    col_signs = [
        mip.LinExpr(list(w), [patterns[k][j] for k in range(len(patterns))], 0)
        for j in range(nc)
    ]
    return model, {"row_signs": row_signs, "col_signs": col_signs}
