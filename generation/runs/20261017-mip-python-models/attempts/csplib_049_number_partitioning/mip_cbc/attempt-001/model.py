# CSPLib 049 number partitioning: partition the numbers 1..N into two sets A and B
# such that A and B have the same cardinality, the same sum, and the same sum of squares.
# Print the sets A and B.
import mip


def build(instance):
    n = instance["n"]
    m = n // 2
    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # a[k][j]: position k of A holds the value j + 1
    a = [[model.add_var(f"a_{k}_{j}", var_type=mip.BINARY) for j in range(n)] for k in range(m)]
    # b[k][j]: position k of B holds the value j + 1
    b = [[model.add_var(f"b_{k}_{j}", var_type=mip.BINARY) for j in range(n)] for k in range(m)]

    # Each position of A holds exactly one number.
    for k in range(m):
        model.add_constr(mip.xsum(a[k][j] for j in range(n)) == 1)

    # Each position of B holds exactly one number.
    for k in range(m):
        model.add_constr(mip.xsum(b[k][j] for j in range(n)) == 1)

    # Every number 1..N is in exactly one of A and B, so A and B partition the numbers.
    for j in range(n):
        model.add_constr(mip.xsum([a[k][j] for k in range(m)] + [b[k][j] for k in range(m)]) == 1)

    # A and B have the same sum.
    model.add_constr(
        mip.xsum((j + 1) * a[k][j] for k in range(m) for j in range(n))
        == mip.xsum((j + 1) * b[k][j] for k in range(m) for j in range(n))
    )

    # A and B have the same sum of squares.
    model.add_constr(
        mip.xsum((j + 1) ** 2 * a[k][j] for k in range(m) for j in range(n))
        == mip.xsum((j + 1) ** 2 * b[k][j] for k in range(m) for j in range(n))
    )

    outputs = {
        "A": [mip.xsum((j + 1) * a[k][j] for j in range(n)) for k in range(m)],
        "B": [mip.xsum((j + 1) * b[k][j] for j in range(n)) for k in range(m)],
    }
    return model, outputs
