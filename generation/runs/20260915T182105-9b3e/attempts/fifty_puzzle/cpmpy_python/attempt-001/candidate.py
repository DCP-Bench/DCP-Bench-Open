import cpmpy as cp


def build(instance):
    """Fifty puzzle: knock over a set of dummies whose numbers total exactly
    the target sum.
    """
    values = instance["values"]
    target_sum = instance["target_sum"]
    n = len(values)

    dummies = cp.boolvar(shape=n, name="dummies")

    model = cp.Model(
        cp.sum([values[i] * dummies[i] for i in range(n)]) == target_sum
    )

    return model, {"dummies": dummies}
