# Archery puzzle: choose how many arrows to put on each target ring, using as many arrows as
# wanted, so that the total score gets as close as possible to the target score.
from exact import Exact


def build(instance):
    targets = instance["targets"]  # points a hit on each ring scores
    target_score = instance["target_score"]  # the total the archer is aiming for
    n = len(targets)

    solver = Exact()

    # hits[i] = number of arrows on ring i; the reference bounds it by the target score
    hits = [f"hits_{i}" for i in range(n)]
    for name in hits:
        solver.addVariable(name, 0, target_score)

    # score = total points scored; deviation = distance from the target score. Both are bounded
    # by twice the target score, as in the reference.
    solver.addVariable("score", 0, 2 * target_score)
    solver.addVariable("deviation", 0, 2 * target_score)

    # the score is the sum of the points of all hits
    solver.addConstraint([(targets[i], hits[i]) for i in range(n) if targets[i]] + [(-1, "score")],
                         True, 0, True, 0)

    # deviation = |target_score - score|. Exact is linear, so the gap is split into an overshoot
    # and an undershoot, and deviation is their sum. Minimising it keeps at most one of the two
    # nonzero: the optimum cannot be reached with both positive.
    solver.addVariable("overshoot", 0, 2 * target_score)
    solver.addVariable("undershoot", 0, 2 * target_score)
    solver.addConstraint([(1, "score"), (-1, "overshoot"), (1, "undershoot")],
                         True, target_score, True, target_score)
    solver.addConstraint([(1, "overshoot"), (1, "undershoot"), (-1, "deviation")], True, 0, True, 0)

    # minimise how far the score is from the target
    return solver, {"hits": hits}, ("minimize", [(1, "deviation")])
