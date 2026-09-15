import cpmpy as cp


def build(instance):
    """Archery puzzle: fire as many arrows as you like at the given targets and
    land as close to the target score as possible.
    """
    targets = instance["targets"]
    target_score = instance["target_score"]
    n = len(targets)

    hits = cp.intvar(0, target_score, shape=n, name="hits")
    score = cp.intvar(0, target_score * 2, name="score")
    deviation = cp.intvar(0, target_score * 2, name="deviation")

    model = cp.Model(
        score == cp.sum(hits * cp.cpm_array(targets)),
        deviation == cp.abs(target_score - score),
    )
    model.minimize(deviation)

    return model, {"hits": hits}
