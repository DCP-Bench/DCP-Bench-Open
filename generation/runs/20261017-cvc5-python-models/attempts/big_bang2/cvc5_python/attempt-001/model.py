# Nontransitive dice (Rock, Paper, Scissors, Lizard, Spock extension).
# Five dice, six faces each, face values in 1..12 (repeats allowed).
# Die A beats die B when A has a strictly larger face than B in more than
# half of the 36 face pairs (strictly more than 18).

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


def build(instance):
    dice = [[cz.Int(f"d_{i}_{f}") for f in range(N_FACES)] for i in range(N_DICE)]

    constraints = []

    # Face values are integers between 1 and 12 inclusive.
    for i in range(N_DICE):
        for f in range(N_FACES):
            constraints.append(dice[i][f] >= MIN_FACE)
            constraints.append(dice[i][f] <= MAX_FACE)

    # The ten 'beats' relationships: die a beats die b when a has a strictly
    # larger face value than b in more than half of all 36 face pairs.
    for a, b in BEATS:
        wins = cz.Sum([
            cz.If(dice[a][fa] > dice[b][fb], 1, 0)
            for fa in range(N_FACES)
            for fb in range(N_FACES)
        ])
        constraints.append(wins > (N_FACES * N_FACES) // 2)

    outputs = {"dice": [[dice[i][f] for f in range(N_FACES)] for i in range(N_DICE)]}
    return constraints, outputs
