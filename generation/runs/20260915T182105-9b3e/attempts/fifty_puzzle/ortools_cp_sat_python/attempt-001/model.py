from ortools.sat.python import cp_model


def build(instance):
    """Fifty puzzle: knock over a set of dummies whose numbers total exactly
    the target sum.
    """
    values = instance["values"]
    target_sum = instance["target_sum"]
    n = len(values)

    model = cp_model.CpModel()
    dummies = [model.new_bool_var(f"d{i}") for i in range(n)]

    model.add(sum(values[i] * dummies[i] for i in range(n)) == target_sum)

    return model, {"dummies": dummies}
