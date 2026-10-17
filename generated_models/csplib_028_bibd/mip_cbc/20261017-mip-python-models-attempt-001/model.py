# Balanced Incomplete Block Design (BIBD) with parameters (v, b, r, k, lambda) from the instance.
# Output "matrix": the v by b incidence matrix of 0/1 values.
import mip


def build(instance):
    v = instance["v"]
    b = instance["b"]
    r = instance["r"]
    k = instance["k"]
    lam = instance["l"]

    m = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")
    x = [[m.add_var(f"x_{i}_{j}", var_type=mip.BINARY) for j in range(b)] for i in range(v)]

    # each object occurs in exactly r different blocks (r ones per row)
    for i in range(v):
        m += mip.xsum(x[i][j] for j in range(b)) == r

    # each block contains exactly k distinct objects (k ones per column)
    for j in range(b):
        m += mip.xsum(x[i][j] for i in range(v)) == k

    # every two distinct objects occur together in exactly lambda blocks
    # (scalar product of any two distinct rows of the incidence matrix is lambda)
    for i in range(v):
        for p in range(i + 1, v):
            z = [m.add_var(f"z_{i}_{p}_{j}", var_type=mip.BINARY) for j in range(b)]
            for j in range(b):
                m += z[j] <= x[i][j]
                m += z[j] <= x[p][j]
                m += z[j] >= x[i][j] + x[p][j] - 1
            m += mip.xsum(z) == lam

    return m, {"matrix": x}
