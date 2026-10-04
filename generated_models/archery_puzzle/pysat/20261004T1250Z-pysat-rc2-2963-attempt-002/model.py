# Archery puzzle: choose how many arrows hit each target ring so that the
# total score comes as close as possible to the target score.
from pysat.formula import IDPool, WCNF
from pysat.integer import Integer, IntegerEngine


def build(instance):
    targets = instance["targets"]
    target_score = instance["target_score"]
    n = len(targets)

    pool = IDPool()
    # hits[i] is the number of arrows on ring i. The reference bounds it by
    # 0..target_score; with the total capped at 2 * target_score (below), a
    # ring worth t can also take at most (2 * target_score) // t arrows, so
    # the tighter of the two bounds is used. Coupled encoding: the runner
    # blocks a reported answer through the value literals, which the order
    # encoding alone does not have.
    hits = []
    for i, t in enumerate(targets):
        ub = target_score if t <= 0 else min(target_score, 2 * target_score // t)
        hits.append(Integer(f"hits_{i}", 0, ub, encoding="coupled", vpool=pool))
    # The total score, 0..2 * target_score as in the reference. Order
    # encoding, so the distance to the target is a run of threshold literals.
    score = Integer("score", 0, 2 * target_score, encoding="order", vpool=pool)
    engine = IntegerEngine(vars=hits + [score], vpool=pool)

    # The score is the sum of the ring values over all arrows shot.
    engine.add_linear(sum(targets[i] * hits[i] for i in range(n)) - score == 0)

    formula = WCNF()
    formula.extend(engine.clausify().clauses)

    # Minimise the deviation |target_score - score|. Overshooting: each
    # threshold v above the target that the score reaches pays 1. Falling
    # short: each threshold v up to the target that the score fails to reach
    # pays 1. Together they pay exactly the distance to the target.
    for v in range(target_score + 1, 2 * target_score + 1):
        formula.append([-score.ge(v)], weight=1)
    for v in range(1, target_score + 1):
        formula.append([score.ge(v)], weight=1)

    return formula, {"hits": hits}
