from ortools.sat.python import cp_model


def build(instance):
    """Archery puzzle: fire as many arrows as you like at the given targets and
    land as close to the target score as possible.
    """
    targets = instance["targets"]
    target_score = instance["target_score"]
    n = len(targets)

    model = cp_model.CpModel()
    hits = [model.new_int_var(0, target_score, f"hits{i}") for i in range(n)]
    # Score and deviation keep the reference's declared bounds.
    score = model.new_int_var(0, target_score * 2, "score")
    deviation = model.new_int_var(0, target_score * 2, "deviation")

    model.add(score == sum(targets[i] * hits[i] for i in range(n)))
    model.add_abs_equality(deviation, target_score - score)
    model.minimize(deviation)

    return model, {"hits": hits}
