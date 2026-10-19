# 0-1 knapsack: a hiker chooses items to take in a backpack. Each item has a value and a
# weight. Maximise the total value of the items taken without exceeding the weight capacity.
# Output x[i] is True when item i is taken.
import mip


def build(instance):
    values = instance["values"]
    weights = instance["weights"]
    capacity = instance["capacity"]
    n = len(values)

    model = mip.Model(sense=mip.MAXIMIZE, solver_name="CBC")
    x = [model.add_var(f"x_{i}", var_type=mip.BINARY) for i in range(n)]

    # The total weight of the items taken does not exceed the weight capacity of the backpack.
    model.add_constr(mip.xsum(weights[i] * x[i] for i in range(n)) <= capacity, "capacity")

    # Maximise the total value of the items taken.
    model.objective = mip.xsum(values[i] * x[i] for i in range(n))

    return model, {"x": x}
