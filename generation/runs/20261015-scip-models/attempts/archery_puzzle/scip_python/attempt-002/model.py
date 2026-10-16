# Archery: choose how many arrows to shoot at each target ring so that the total
# score is as close as possible to the target score; minimise the deviation.
from pyscipopt import Model, quicksum


def build(instance):
    # ring values, one per target, and the score to get as close to as possible
    ring = instance["targets"]
    goal = instance["target_score"]
    n = len(ring)
    t_max = max(ring)

    model = Model()

    # hits[k] = number of arrows on target k (unbounded count, bounded below by the argument below)
    # Bound from the problem: in an optimal shot the total is at most goal + t_max, since
    # removing an arrow whose ring is at most t_max would otherwise lower the deviation.
    # So hits[k] <= (goal + t_max) // ring[k] holds for every optimum.
    hits = [
        model.addVar(name=f"hits_{k}", vtype="I", lb=0, ub=(goal + t_max) // ring[k])
        for k in range(n)
    ]

    # total score of all arrows
    total = quicksum(ring[k] * hits[k] for k in range(n))

    # deviation = |total - goal|, linearised with two inequalities
    dev = model.addVar(name="deviation", vtype="I", lb=0)

    # the total is at least the goal minus the deviation
    model.addCons(total - goal <= dev)
    # the total is at most the goal plus the deviation
    model.addCons(goal - total <= dev)

    # the objective is the distance of the total score from the target score
    model.setObjective(dev, "minimize")

    # the output gives the number of hits per target
    outputs = {"hits": hits}
    return model, outputs
