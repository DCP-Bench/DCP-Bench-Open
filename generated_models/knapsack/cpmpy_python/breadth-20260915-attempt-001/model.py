import cpmpy as cp


def build(instance):
    values, weights = instance["values"], instance["weights"]
    capacity = instance["capacity"]
    chosen = cp.boolvar(shape=len(values), name="x")
    model = cp.Model(cp.sum([w * chosen[i] for i, w in enumerate(weights)]) <= capacity)
    model.maximize(cp.sum([v * chosen[i] for i, v in enumerate(values)]))
    return model, {"x": [chosen[i] for i in range(len(values))]}
