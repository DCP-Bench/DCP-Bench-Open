# Eighteen-hole golf course: each hole has length 3, 4 or 5 and the holes sum to 72.
# The hole count and the total are fixed by the problem statement, not by the instance.
from paramita.modelling import Bool

HOLES = 18
LENGTHS = [3, 4, 5]
TOTAL = 72


def build(instance):
    # One-hot encoding: h[i][v] is true when hole i has length v.
    h = [{v: Bool(f"hole_{i}_len_{v}") for v in LENGTHS} for i in range(HOLES)]

    cons = []
    # each hole has a length of 3, 4, or 5: exactly one length per hole
    cons += [sum(h[i].values()) == 1 for i in range(HOLES)]

    # the total length of the course is 72
    cons += [sum(v * h[i][v] for i in range(HOLES) for v in LENGTHS) == TOTAL]

    # the length of each hole, as an integer expression
    holes = [sum(v * h[i][v] for v in LENGTHS) for i in range(HOLES)]

    return cons, {"holes": holes}
