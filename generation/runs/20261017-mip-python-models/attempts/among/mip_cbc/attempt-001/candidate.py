# Problem "among": choose x[0..n-1], each x[i] an integer in 0..7, such that
# exactly m entries of x take one of the values in v. Print the array x.
# Model built from the instance: n, m and v are read from the instance.
import mip


def build(instance):
    n = instance["n"]
    m_count = instance["m"]
    values = instance["v"]

    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # Domain of every entry of x: 0..7 (fixed by the description).
    domain = range(0, 8)

    # One-hot binaries: p[i][k] = 1 means x[i] takes value k.
    p = [[model.add_var(f"p_{i}_{k}", var_type=mip.BINARY) for k in domain] for i in range(n)]

    # Integer entries x[i], tied to the one-hot choice by an equality row.
    x = [model.add_var(f"x_{i}", lb=0, ub=7, var_type=mip.INTEGER) for i in range(n)]

    # Each entry takes exactly one value of the domain.
    for i in range(n):
        model += mip.xsum(p[i][k] for k in domain) == 1
        model += x[i] == mip.xsum(k * p[i][k] for k in domain)

    # Requires exactly m values in x to take one of the values in v.
    # Membership of x[i] in v is the sum of the one-hot binaries of the values in v.
    in_set = sorted({val for val in values if 0 <= val <= 7})
    member = [mip.xsum(p[i][k] for k in in_set) for i in range(n)]
    model += mip.xsum(member) == m_count

    # Satisfaction problem: no objective is set.
    return model, {"x": x}
