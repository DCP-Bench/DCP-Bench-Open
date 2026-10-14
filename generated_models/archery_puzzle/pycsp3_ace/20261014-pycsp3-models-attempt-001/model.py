from pycsp3 import *

# The young archer shoots at several rings; each arrow on ring i scores targets[i].
# She may shoot as many arrows as she likes. We find how many hits per ring get
# her total as close as possible to the target score.

targets = data.targets
target_score = data.target_score
n = len(targets)

# hits[i] is the number of arrows that land on ring i
# (a total above twice the target cannot be optimal, because shooting nothing
# already gives deviation target_score, so each ring is bounded by that total)
hits = VarArray(size=n, dom=range(0, 2 * target_score // min(targets) + 1))

# deviation is the distance between her total and the target score
deviation = Var(dom=range(0, target_score + 1))

satisfy(
    # no ring can be hit more often than a total of twice the target allows
    [hits[i] <= 2 * target_score // targets[i] for i in range(n)],
    # the total may overshoot the target score; the deviation bounds the overshoot
    Sum(targets[i] * hits[i] for i in range(n)) - target_score <= deviation,
    # the total may undershoot the target score; the deviation bounds the undershoot
    target_score - Sum(targets[i] * hits[i] for i in range(n)) <= deviation,
)

# minimise how far the total score is from the target score
minimize(deviation)
