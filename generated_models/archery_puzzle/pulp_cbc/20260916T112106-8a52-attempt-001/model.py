import pulp


def build(instance):
    """Archery puzzle: fire as many arrows as you like at the given targets and
    land as close to the target score as possible.
    """
    targets = instance["targets"]
    target_score = instance["target_score"]
    n = len(targets)

    problem = pulp.LpProblem("archery", pulp.LpMinimize)
    hits = [pulp.LpVariable(f"h{i}", 0, target_score, cat="Integer")
            for i in range(n)]
    score = pulp.LpVariable("score", 0, target_score * 2, cat="Integer")
    deviation = pulp.LpVariable("deviation", 0, target_score * 2, cat="Integer")

    problem += score == pulp.lpSum(targets[i] * hits[i] for i in range(n))
    # Under minimization the two bounds are enough to pin the absolute value.
    problem += deviation >= target_score - score
    problem += deviation >= score - target_score
    problem += deviation

    return problem, {"hits": hits}
