"""Nontransitive dice: five six-faced dice whose 'beats' relation is Rock-Paper-Scissors-Lizard-Spock.

Each face takes a value in 1..12, encoded in order (unary) form: ge[t] means "face >= t" for t = 2..12.
Die A beats die B when A has a strictly larger face than B in more than half of the 36 face pairs,
i.e. in at least 19 of the pairs.
"""

from paramita.modelling import Bool, If, Or

FACES = 6
LOW, HIGH = 1, 12
# Dice indices: 0 Rock, 1 Paper, 2 Scissors, 3 Lizard, 4 Spock.
# Each pair is (winner, loser) as in the problem statement.
BEATS = [
    (0, 2), (0, 3),  # Rock crushes Scissors, Rock crushes Lizard
    (1, 0), (1, 4),  # Paper covers Rock, Paper disproves Spock
    (2, 1), (2, 3),  # Scissors cuts Paper, Scissors decapitate Lizard
    (3, 1), (3, 4),  # Lizard eats Paper, Lizard poisons Spock
    (4, 0), (4, 2),  # Spock vaporizes Rock, Spock smashes Scissors
]
DICE = 5
THRESHOLDS = range(LOW + 1, HIGH + 1)  # t = 2..12: "face >= t"


def build(instance):
    # Order encoding: ge[d, k][t] is "face k of die d is at least t".
    ge = {}
    for d in range(DICE):
        for k in range(FACES):
            ge[d, k] = {t: Bool(f"face_{d}_{k}_ge_{t}") for t in THRESHOLDS}

    cons = []

    # the thresholds are nested: a face at least t is at least t-1
    for d in range(DICE):
        for k in range(FACES):
            for t in range(LOW + 2, HIGH + 1):
                cons.append(If(ge[d, k][t], ge[d, k][t - 1]))

    # the face value as an integer expression: 1 plus the number of thresholds it passes
    value = {(d, k): 1 + sum(ge[d, k].values()) for d in range(DICE) for k in range(FACES)}

    # a face of die a is strictly larger than a face of die b when for some t it is at least t and b is below t
    def larger(a_key, b_key):
        return Or([ge[a_key][t] & ~ge[b_key][t] for t in THRESHOLDS])

    # die A beats die B when A has a strictly larger face in more than half of the 36 face pairs
    for a, b in BEATS:
        wins = []
        for i in range(FACES):
            for j in range(FACES):
                gt = Bool(f"larger_{a}_{i}_{b}_{j}")
                # gt can only be true when face i of die a is larger than face j of die b
                cons.append(If(gt, larger((a, i), (b, j))))
                wins.append(gt)
        # more than half of the 36 pairs: at least 19 of them
        cons.append(sum(wins) >= 19)

    dice = [[value[d, k] for k in range(FACES)] for d in range(DICE)]
    return cons, {"dice": dice}
