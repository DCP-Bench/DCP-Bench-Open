# Magic sequence (CSPLib 019): find x_0..x_{n-1}, each between 0 and n-1, such that
# for every i the number i occurs exactly x_i times in the sequence.
import mip


def build(instance):
    # n is the sequence length, read from the instance.
    n = instance["n"]
    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # x[i] is the i-th element of the sequence, a value in 0..n-1 (from the problem statement)
    x = [model.add_var(f"x_{i}", lb=0, ub=n - 1, var_type=mip.INTEGER) for i in range(n)]

    # v[j][k] = 1 if element x_j takes the value k (one-hot encoding of x_j)
    v = [[model.add_var(f"v_{j}_{k}", var_type=mip.BINARY) for k in range(n)] for j in range(n)]

    # each element of the sequence takes exactly one value
    for j in range(n):
        model += mip.xsum(v[j]) == 1
        # x_j is the value its one-hot choice selects
        model += x[j] == mip.xsum(k * v[j][k] for k in range(n))

    # the number i occurs exactly x_i times in the sequence:
    # x_i equals the count of positions j whose value is i
    for i in range(n):
        model += x[i] == mip.xsum(v[j][i] for j in range(n))

    # satisfaction problem: no objective
    return model, {"x": x}
