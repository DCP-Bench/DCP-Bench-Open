# Maximise the value carried without exceeding the knapsack capacity.
from hermax.model import Model


def build(instance):
    values = instance["values"]
    weights = instance["weights"]
    capacity = instance["capacity"]
    n = len(values)

    m = Model()
    x = m.bool_vector("x", n)
    m &= (sum(weights[j] * x[j] for j in range(n)) <= capacity)

    # Maximising: every item left behind costs its value, so the least value
    # forgone is the most value carried.
    for j in range(n):
        m.obj[values[j]] += x[j]
    return m, {"x": x}
