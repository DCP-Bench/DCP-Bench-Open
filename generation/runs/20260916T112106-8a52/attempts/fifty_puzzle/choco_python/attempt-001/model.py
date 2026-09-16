from pychoco.model import Model


def build(instance):
    """Fifty puzzle: knock over a set of dummies whose numbers total exactly
    the target sum.
    """
    values = instance["values"]
    target_sum = instance["target_sum"]
    n = len(values)

    model = Model()
    dummies = [model.boolvar(name=f"d{i}") for i in range(n)]
    model.scalar(dummies, values, "=", target_sum).post()

    return model, {"dummies": dummies}
