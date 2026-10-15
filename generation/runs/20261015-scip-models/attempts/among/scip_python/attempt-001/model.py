# Among: choose an array x of n values in 0..7 such that exactly m entries of x take a value from v.
from pyscipopt import Model, quicksum

# Problem constant: every entry of x is between 0 and 7 (from the problem statement).
MAX_VALUE = 7


def build(instance):
    n = instance["n"]  # length of x
    m_count = instance["m"]  # number of entries of x that must take a value in v
    allowed = sorted(set(instance["v"]))  # the allowed values; set() guards against repeats

    model = Model()

    # value[i, k] = 1 if x[i] takes the value k (one-hot encoding of x[i])
    value = {(i, k): model.addVar(name=f"value_{i}_{k}", vtype="B")
             for i in range(n) for k in range(MAX_VALUE + 1)}
    # x[i] is an integer expression over its one-hot binaries
    x = [quicksum(k * value[i, k] for k in range(MAX_VALUE + 1)) for i in range(n)]

    # each entry of x takes exactly one value between 0 and 7
    for i in range(n):
        model.addCons(quicksum(value[i, k] for k in range(MAX_VALUE + 1)) == 1)

    # in_v[i] = 1 if x[i] takes one of the values in v (equals the sum of its one-hot binaries over v)
    in_v = [quicksum(value[i, k] for k in allowed) for i in range(n)]

    # exactly m entries of x take a value in v
    model.addCons(quicksum(in_v) == m_count)

    # the output is the array x
    return model, {"x": x}
