from pychoco.model import Model


def build(instance):
    """Knapsack: pick items to maximize total value without exceeding the
    pack's weight capacity.
    """
    values = instance["values"]
    weights = instance["weights"]
    capacity = instance["capacity"]
    n = len(values)

    model = Model()
    take = [model.boolvar(name=f"take{i}") for i in range(n)]

    model.scalar(take, weights, "<=", capacity).post()

    total = model.intvar(0, sum(values), name="total")
    model.scalar(take, values, "=", total).post()

    return model, {"x": take}, ("maximize", total)
