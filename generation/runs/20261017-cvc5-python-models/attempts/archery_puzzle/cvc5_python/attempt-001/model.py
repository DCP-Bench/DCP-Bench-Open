# Archery puzzle: how close can a young archer come to a target total score,
# shooting as many arrows as she pleases at targets with given ring scores?
# Output the number of hits on each target (hits). Minimise the deviation
# between the total score and the target score.
import cvc5.pythonic as cz


def build(instance):
    targets = instance["targets"]
    target_score = instance["target_score"]
    n = len(targets)

    hits = [cz.Int(f"hits_{i}") for i in range(n)]
    dev = cz.Int("dev")

    # Number of arrows on each target is a non-negative integer.
    # An optimal solution never uses more than target // t + 1 arrows on a
    # target of score t: one arrow fewer would still overshoot the target score,
    # so it would be strictly closer.
    cons = []
    for h, t in zip(hits, targets):
        cons += [h >= 0, h <= target_score // t + 1]

    # Each arrow on target i scores targets[i]; the archer uses as many arrows
    # as she pleases, and the total score is the sum of hits times ring scores.
    total = cz.Sum([h * t for h, t in zip(hits, targets)])

    # The deviation is the absolute difference between the total score and the
    # target score. It is minimised.
    cons += [dev >= 0, dev >= total - target_score, dev >= target_score - total]

    s = cz.SolverFor("QF_LIA")
    s.add(*cons)
    return s, {"hits": hits}, ("minimize", dev)
