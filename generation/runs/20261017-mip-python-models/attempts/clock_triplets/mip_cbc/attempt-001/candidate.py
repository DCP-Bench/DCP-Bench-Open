# Clock triplets: rearrange the numbers 1 to 12 on the face of a clock so that no
# triplet of adjacent numbers has a sum higher than 21. Output x lists the 12 numbers
# in clock order. Satisfaction problem.
import mip


def build(instance):
    n = 12
    values = list(range(1, n + 1))
    m = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # Position i holds one of the numbers 1 to 12. One-hot binaries p[i][k] pick the value k+1.
    p = [[m.add_var(f"p_{i}_{k}", var_type=mip.BINARY) for k in range(n)] for i in range(n)]
    x = [m.add_var(f"x_{i}", lb=1, ub=n, var_type=mip.INTEGER) for i in range(n)]

    # Each position holds exactly one number, tied to the output by an equality row.
    for i in range(n):
        m += mip.xsum(p[i]) == 1
        m += x[i] == mip.xsum(v * p[i][k] for k, v in enumerate(values))

    # The numbers on the clock are all different: the numbers 1 to 12 each appear once.
    for k in range(n):
        m += mip.xsum(p[i][k] for i in range(n)) == 1

    # No triplet of adjacent numbers on the clock has a sum higher than 21 (the clock wraps around).
    for i in range(n):
        m += x[i] + x[(i + 1) % n] + x[(i + 2) % n] <= 21

    return m, {"x": x}
