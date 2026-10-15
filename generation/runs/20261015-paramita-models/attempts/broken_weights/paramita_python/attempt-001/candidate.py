# Broken weights: a measuring weight broke into n whole-pound pieces that can
# weigh every integer from 1 to the total weight m on a balance scale, where
# pieces can go on either pan. Find the piece weights.
from paramita.modelling import Bool, Or, If


def any_of(xs):
    return xs[0] if len(xs) == 1 else Or(xs)


def build(instance):
    m, n = instance["m"], instance["n"]

    # one-hot integer per piece: x[i][v] is true when piece i weighs v pounds
    x = [[Bool(f"x_{i}_{v}") for v in range(1, m + 1)] for i in range(n)]
    w = [sum(v * x[i][v - 1] for v in range(1, m + 1)) for i in range(n)]
    cons = []

    # each piece weighs exactly one whole number of pounds
    cons += [sum(x[i]) == 1 for i in range(n)]

    # the pieces together make up the whole weight m
    cons.append(sum(w) == m)

    # pieces have distinct weights (all-different, as in the reference;
    # the instance notes say no valid answer is excluded by this)
    cons += [w[i] < w[i + 1] for i in range(n - 1)]

    # every integer t in 1..m is a balance of pieces: each piece is on the
    # weighing pan, on the other pan, or off the scale, so t is a signed sum.
    # reach[i][s] (over the first i pieces) means the signed sum s is possible.
    # Only the implication from reach to a witness is needed: the empty sum 0
    # is always possible, so every true reach is backed by a chain of placements.
    empty = Bool("reach_0_0")
    cons.append(empty)
    prev = {0: empty}  # layer 0: only the empty sum
    for i in range(n):
        cur = {}
        for s in range(-m, m + 1):
            options = []
            if s in prev:
                options.append(prev[s])  # piece i is off the scale
            for v in range(1, m + 1):
                # piece i adds v (other pan: subtracts v), so the earlier sum was s - v or s + v
                srcs = [prev[t] for t in (s - v, s + v) if t in prev]
                if srcs:
                    options.append(x[i][v - 1] & any_of(srcs))
            if not options:
                continue
            r = Bool(f"reach_{i + 1}_{s + m}")
            cur[s] = r
            cons.append(If(r, any_of(options)))
        prev = cur

    # the final layer must reach every weight from 1 to m
    for t in range(1, m + 1):
        if t not in prev:
            raise ValueError("no way to weigh %d" % t)
        cons.append(prev[t])

    return cons, {"weights": w}
