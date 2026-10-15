from paramita.modelling import Bool, If

# Archery puzzle: a young archer shoots as many arrows as she likes at several
# targets. An arrow on target i scores targets[i]. Choose the number of hits on
# each target so that the total score is as close as possible to target_score,
# whether it is above or below.


def build(instance):
    target_score = instance["target_score"]
    targets = instance["targets"]
    m = len(targets)
    top = max(targets)

    # hits on target i, in unary: ge[i][k] is true when hits[i] >= k + 1.
    # The bound comes from the optimum: with total >= target_score + top, removing
    # one arrow would get closer, so every optimal total is below target_score + top
    # and hits[i] <= (target_score + top - 1) // targets[i].
    ge = []
    for i in range(m):
        width = (target_score + top - 1) // targets[i]
        ge.append([Bool(f"hit_{i}_ge_{k + 1}") for k in range(width)])
    cons = []
    for i in range(m):
        # the true values come first, so the unary bits count the hits
        for k in range(len(ge[i]) - 1):
            cons.append(If(ge[i][k + 1], ge[i][k]))
    hits = [sum(ge[i]) for i in range(m)]

    # total score: an arrow on target i scores targets[i]
    total = sum(targets[i] * b for i in range(m) for b in ge[i])

    # overshoot above the target, in unary; it is at most top - 1 at the optimum
    over = [Bool(f"over_ge_{k + 1}") for k in range(top)]
    for k in range(len(over) - 1):
        cons.append(If(over[k + 1], over[k]))
    # undershoot below the target, in unary; at most target_score
    under = [Bool(f"under_ge_{k + 1}") for k in range(target_score)]
    for k in range(len(under) - 1):
        cons.append(If(under[k + 1], under[k]))

    # the total minus the target does not exceed the overshoot
    cons.append(total - sum(over) <= target_score)
    # the target minus the total does not exceed the undershoot
    cons.append(total + sum(under) >= target_score)

    # the deviation |total - target_score| is the overshoot plus the undershoot
    deviation = sum(over) + sum(under)

    return cons, {"hits": hits}, ("minimize", deviation)
