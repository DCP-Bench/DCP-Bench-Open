# Archery puzzle: choose how many arrows to put on each target ring so that the
# total score is as close as possible to a given target score.
import z3


def build(instance):
    targets = instance["targets"]            # points scored by one arrow on each ring
    target_score = instance["target_score"]  # the total the archer aims for
    n = len(targets)

    # hits[i] is the number of arrows on ring i. Any arrow scores at least 1 point,
    # so at most target_score arrows are useful; this is the reference's bound.
    hits = [z3.Int(f"hits_{i}") for i in range(n)]
    # score is the total scored and deviation how far it is from the target.
    score = z3.Int("score")
    deviation = z3.Int("deviation")

    solver = z3.Solver()

    for h in hits:
        solver.add(h >= 0, h <= target_score)
    # Bounds on the total and on the deviation, as in the reference (twice the target).
    solver.add(score >= 0, score <= 2 * target_score)
    solver.add(deviation >= 0, deviation <= 2 * target_score)

    # The total score is the sum of arrows on each ring times that ring's points.
    solver.add(score == z3.Sum([hits[i] * targets[i] for i in range(n)]))
    # The deviation is the distance between the target and the total score.
    solver.add(deviation == z3.Abs(target_score - score))

    # Come as close to the target score as possible.
    return solver, {"hits": hits}, ("minimize", deviation)
