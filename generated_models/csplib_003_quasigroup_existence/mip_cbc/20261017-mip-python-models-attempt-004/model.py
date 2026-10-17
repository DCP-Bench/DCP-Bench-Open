# csplib_003, quasigroup existence (QG3.m): find an order-m quasigroup, an m x m table
# over the values 0..m-1 in which each element occurs once in every row and column,
# with (a*b)*(b*a) = a for all a, b. The output is the table quasigroup[i][j] = i*j.
import mip


def build(instance):
    m = instance["m"]
    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")
    pass
    vals = range(m)

    # Pair images. phi(a, b) = (a*b, b*a). The QG3 condition (a*b)*(b*a) = a says that phi
    # is an involution: phi(a, b) = (k, l) implies phi(k, l) = (a, b). Also phi(b, a) is the
    # swap of phi(a, b). Variable p[a,b,k,l] = 1 iff phi(a, b) = (k, l). The four index
    # tuples (a,b,k,l), (k,l,a,b), (b,a,l,k), (l,k,b,a) describe the same fact, so they share
    # one binary. The QG3 rows are then implied and need no separate constraints.
    def key(a, b, k, l):
        return min((a, b, k, l), (k, l, a, b), (b, a, l, k), (l, k, b, a))

    pv = {}
    for a in vals:
        for b in vals:
            for k in vals:
                for l in vals:
                    t = key(a, b, k, l)
                    if t not in pv:
                        pv[t] = model.add_var(
                            f"p_{t[0]}_{t[1]}_{t[2]}_{t[3]}", var_type=mip.BINARY)

    def p(a, b, k, l):
        return pv[key(a, b, k, l)]

    # The table entries: x[i][j][v] = 1 iff i*j = v (one-hot), q[i][j] = i*j as an integer.
    x = [[[model.add_var(f"x_{i}_{j}_{v}", var_type=mip.BINARY) for v in vals]
          for j in vals] for i in vals]
    q = [[model.add_var(f"q_{i}_{j}", lb=0, ub=m - 1, var_type=mip.INTEGER)
          for j in vals] for i in vals]

    # The table is an m x m multiplication table: each cell holds one element.
    for i in vals:
        for j in vals:
            model += mip.xsum(x[i][j][v] for v in vals) == 1
            model += q[i][j] == mip.xsum(v * x[i][j][v] for v in vals)

    # Each element occurs once in every row.
    for i in vals:
        for v in vals:
            model += mip.xsum(x[i][j][v] for j in vals) == 1

    # Each element occurs once in every column.
    for j in vals:
        for v in vals:
            model += mip.xsum(x[i][j][v] for i in vals) == 1

    # The table entry a*b = k is the sum of the pair images of (a, b) whose first part is k.
    # Through the shared variables this also fixes b*a, since phi(b, a) is the swap.
    for a in vals:
        for b in vals:
            for k in vals:
                model += x[a][b][k] == mip.xsum(p(a, b, k, l) for l in vals)

    # Implied by QG3: phi is an involution, so it is a bijection on pairs. Each pair (k, l)
    # is the image of exactly one (a, b).
    for k in vals:
        for l in vals:
            model += mip.xsum(p(a, b, k, l) for a in vals for b in vals) == 1

    for a in vals:
        for b in vals:
            model += mip.xsum(p(a, b, k, l) for k in vals for l in vals) == 1

    # Implied by QG3 with a = b: d(a) = a*a satisfies d(d(a)) = a, so d is a permutation.
    # Each value c is the diagonal entry a*a for exactly one a.
    for c in vals:
        model += mip.xsum(x[a][a][c] for a in vals) == 1

    return model, {"quasigroup": q}
