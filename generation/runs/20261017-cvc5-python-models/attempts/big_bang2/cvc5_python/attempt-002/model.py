# Nontransitive dice (Rock, Paper, Scissors, Lizard, Spock extension).
# Five dice, six faces each, face values in 1..12 (repeats allowed).
# Die A beats die B when A has a strictly larger face value than B in more
# than half of all possible pairs of faces (more than 18 of the 36 pairs).
#
# Encoding: purely Boolean. Each face value is an order encoding (one Boolean
# per threshold 2..12), each face-pair comparison is a reified Boolean, and
# the "more than half" count is a sequential counter over those Booleans.

import itertools

import cvc5.pythonic as cz

# Choice indices: 0 Rock, 1 Paper, 2 Scissors, 3 Lizard, 4 Spock.
BEATS = [
    (0, 2), (0, 3),  # Rock crushes Scissors, Rock crushes Lizard
    (1, 0), (1, 4),  # Paper covers Rock, Paper disproves Spock
    (2, 1), (2, 3),  # Scissors cuts Paper, Scissors decapitate Lizard
    (3, 1), (3, 4),  # Lizard eats Paper, Lizard poisons Spock
    (4, 0), (4, 2),  # Spock vaporizes Rock, Spock smashes Scissors
]

N_DICE = 5
N_FACES = 6
MIN_FACE = 1
MAX_FACE = 12
PAIRS = N_FACES * N_FACES
NEEDED_WINS = PAIRS // 2 + 1  # strictly more than half of the face pairs


def build(instance):
    counter = itertools.count()

    def fresh(prefix):
        return cz.Bool(f"{prefix}_{next(counter)}")

    constraints = []

    # Each face value is an integer between 1 and 12 inclusive.
    # ge[i][f][v] holds exactly when face f of die i is at least v (v = 2..12);
    # the value 1 needs no variable, and the order encoding keeps it within 1..12.
    ge = [
        [{v: fresh("ge") for v in range(2, MAX_FACE + 1)} for _ in range(N_FACES)]
        for _ in range(N_DICE)
    ]
    for i in range(N_DICE):
        for f in range(N_FACES):
            for v in range(2, MAX_FACE):
                constraints.append(cz.Implies(ge[i][f][v + 1], ge[i][f][v]))

    def value(i, f):
        return 1 + cz.Sum([cz.If(ge[i][f][v], 1, 0) for v in range(2, MAX_FACE + 1)])

    def greater(i, fi, j, fj):
        # Reified Boolean: face fi of die i is strictly larger than face fj of die j.
        # a > b exactly when some threshold v has a >= v and not b >= v.
        g = fresh("gt")
        constraints.append(
            g == cz.Or([cz.And(ge[i][fi][v], cz.Not(ge[j][fj][v]))
                        for v in range(2, MAX_FACE + 1)])
        )
        return g

    def at_least(bools, k):
        # Sequential counter: row j holds "at least j of the Booleans seen so far".
        prev = {j: fresh("cnt") for j in range(1, k + 1)}
        for j in range(1, k + 1):
            constraints.append(cz.Not(prev[j]))
        for x in bools:
            cur = {}
            for j in range(1, k + 1):
                cur[j] = fresh("cnt")
                if j == 1:
                    rhs = cz.Or(prev[1], x)
                else:
                    rhs = cz.Or(prev[j], cz.And(prev[j - 1], x))
                constraints.append(cur[j] == rhs)
            prev = cur
        constraints.append(prev[k])

    # A has a strictly larger face value than die B in more than half of all
    # possible pairs of faces, for each of the ten 'beats' relationships.
    for a, b in BEATS:
        wins = [
            greater(a, fa, b, fb)
            for fa in range(N_FACES)
            for fb in range(N_FACES)
        ]
        at_least(wins, NEEDED_WINS)

    # Print the dice: row 0 is Rock, row 1 Paper, row 2 Scissors, row 3 Lizard, row 4 Spock.
    outputs = {"dice": [[value(i, f) for f in range(N_FACES)] for i in range(N_DICE)]}
    return constraints, outputs
