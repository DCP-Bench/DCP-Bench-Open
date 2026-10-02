# Archery puzzle: choose how many arrows to put on each target ring so that the
# total score is as close as possible to a given target score.
import z3


def build(instance):
    targets = instance["targets"]            # points scored by one arrow on each ring
    target_score = instance["target_score"]  # the total the archer aims for
    n = len(targets)

    # hits[i] is the number of arrows on ring i.
    hits = [z3.Int(f"hits_{i}") for i in range(n)]
    # score is the total scored and deviation how far it is from the target.
    score = z3.Int("score")
    deviation = z3.Int("deviation")

    solver = z3.Solver()

    # Arrows on a ring: at least 0, and at most target_score (the reference's bound).
    # Because the total score may not exceed twice the target (below), ring i can
    # also take at most 2 * target_score // targets[i] arrows. This implied bound
    # keeps Z3 from branching over a much larger range on the equation for score.
    for i in range(n):
        top = target_score
        if targets[i] > 0:
            top = min(top, 2 * target_score // targets[i])
        solver.add(hits[i] >= 0, hits[i] <= top)
    # Bounds on the total and on the deviation, as in the reference (twice the target).
    solver.add(score >= 0, score <= 2 * target_score)
    solver.add(deviation >= 0, deviation <= 2 * target_score)

    # The total score is the sum of arrows on each ring times that ring's points.
    solver.add(score == z3.Sum([hits[i] * targets[i] for i in range(n)]))
    # The deviation is the distance between the target and the total score.
    solver.add(deviation == z3.Abs(target_score - score))

    # Come as close to the target score as possible.
    return solver, {"hits": hits}, ("minimize", deviation)
