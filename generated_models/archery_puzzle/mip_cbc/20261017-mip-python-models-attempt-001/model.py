# Archery puzzle: a young archer shoots as many arrows as she likes at targets.
# Each arrow on target i scores targets[i]. How close can the total come to
# target_score? Output hits: the number of arrows on each target.
import mip


def build(instance):
    targets = instance["targets"]
    target = instance["target_score"]
    n = len(targets)

    m = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # Shoot as many arrows as she likes at each target. The empty shooting already
    # misses by target_score, so an optimal total is at most 2 * target_score, which
    # bounds the number of arrows on target i.
    hits = [
        m.add_var(f"hits_{i}", lb=0, ub=(2 * target) // targets[i], var_type=mip.INTEGER)
        for i in range(n)
    ]
    total = mip.xsum(targets[i] * hits[i] for i in range(n))

    # The deviation is how close the total comes to target_score: the absolute
    # difference between the total score and the target score.
    dev = m.add_var("dev", lb=0, ub=target, var_type=mip.INTEGER)
    m += dev >= total - target
    m += dev >= target - total

    # How close can she come: minimise the deviation.
    m.objective = dev

    return m, {"hits": hits}
