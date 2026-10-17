# Problem "among": an array x of length n, each entry an integer between 0 and 7.
# Requires exactly m values in x to take one of the values in v.
# n, m and v are read from the instance. Print the array x.
import mip


def build(instance):
    n = instance["n"]
    m = instance["m"]
    v = instance["v"]

    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # All other values may be anything from 0 to 7 (the domain stated in the description).
    x = [model.add_var(f"x_{i}", lb=0, ub=7, var_type=mip.INTEGER) for i in range(n)]

    # Selector binaries: pick[i][k] = 1 when x[i] equals the value k, for k from 0 to 7.
    pick = [[model.add_var(f"pick_{i}_{k}", var_type=mip.BINARY) for k in range(8)] for i in range(n)]
    for i in range(n):
        # x[i] takes exactly one value between 0 and 7.
        model += mip.xsum(pick[i][k] for k in range(8)) == 1
        model += x[i] == mip.xsum(k * pick[i][k] for k in range(8))

    # Requires exactly m values in x to take one of the values in v.
    # A value of x[i] is in v when its selector for one of the values of v is set.
    in_v = sorted({val for val in v if 0 <= val <= 7})
    model += mip.xsum(pick[i][k] for i in range(n) for k in in_v) == m

    # No objective: this is a satisfaction problem.
    return model, {"x": x}
