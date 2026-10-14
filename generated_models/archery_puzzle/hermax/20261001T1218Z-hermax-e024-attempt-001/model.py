# Archery puzzle: an archer may shoot as many arrows as she likes at targets
# worth given scores. Choose how many arrows hit each target so that the total
# score is as close as possible to the target score.
from hermax.model import Model


def build(instance):
    targets = instance["targets"]  # points for a hit on each target
    goal = instance["target_score"]  # the total score the archer aims for
    n = len(targets)

    m = Model()
    # hits[i] = number of arrows that hit target i. A total above 2 * goal is
    # never the best (zero arrows is already within `goal` of the goal), so the
    # number of hits is capped where its own score reaches 2 * goal, and by the
    # problem's own bound of `goal` arrows per target. (The cap is kept at 1 or
    # more so the domain is never a single value; the deviation bound below
    # rules out any shot that is too high.)
    hits = [m.int(f"hits_{i}", 0, max(1, min(goal, 2 * goal // targets[i]))) for i in range(n)]

    # deviation = how far the total is from the goal, between 0 and goal
    # (the best deviation is at most goal, by shooting nothing)
    deviation = m.int("deviation", 0, goal)
    total = sum(targets[i] * hits[i] for i in range(n))
    # The deviation is at least goal - total and at least total - goal. It is only
    # bounded below here and the objective pushes it down to the true distance;
    # this avoids tying the total to an integer variable with an equality.
    m &= (deviation + total >= goal)
    m &= (total - deviation <= goal)

    # Minimise the deviation: it is charged one per unit, each unit k being paid
    # when deviation >= k holds. The soft clause is the negation of that, since a
    # soft clause pays when its literal is false.
    for k in range(1, goal + 1):
        m.obj[1] += ~(deviation >= k)

    return m, {"hits": hits}
