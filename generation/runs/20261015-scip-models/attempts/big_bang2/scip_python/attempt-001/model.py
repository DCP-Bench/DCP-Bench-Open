# Nontransitive dice: find five six-faced dice (faces 1..12) whose 'beats'
# relation matches the ten Rock-Paper-Scissors-Lizard-Spock relations.

from pyscipopt import Model, quicksum

# Die indices, in the order the output lists them.
ROCK, PAPER, SCISSORS, LIZARD, SPOCK = 0, 1, 2, 3, 4
FACES = 6
MIN_FACE, MAX_FACE = 1, 12

# The ten 'beats' relations of the description, as (winner, loser) pairs.
BEATS = [
    (ROCK, SCISSORS),      # Rock crushes Scissors
    (ROCK, LIZARD),        # Rock crushes Lizard
    (PAPER, ROCK),         # Paper covers Rock
    (PAPER, SPOCK),        # Paper disproves Spock
    (SCISSORS, PAPER),     # Scissors cuts Paper
    (SCISSORS, LIZARD),    # Scissors decapitate Lizard
    (LIZARD, PAPER),       # Lizard eats Paper
    (LIZARD, SPOCK),       # Lizard poisons Spock
    (SPOCK, ROCK),         # Spock vaporizes Rock
    (SPOCK, SCISSORS),     # Spock smashes Scissors
]

def build(instance):
    m = Model()

    # x[d, f]: value of face f of die d
    x = {(d, f): m.addVar(name=f"x_{d}_{f}", vtype="I", lb=MIN_FACE, ub=MAX_FACE)
         for d in range(5) for f in range(FACES)}

    # Winning pairs of faces must be at least half of all 36 face pairs
    # (strictly more than half, so at least 19 of 36 pairs).
    # g[a, b, f, g2] = 1 forces face f of die a to be strictly larger than
    # face g2 of die b. Only this direction is needed: a lower bound on
    # the number of winning face pairs is enough.
    for (a, b) in BEATS:
        # the winner's face beats the loser's face in more than half of the face pairs
        wins = []
        for f in range(FACES):
            for g2 in range(FACES):
                g = m.addVar(name=f"win_{a}_{b}_{f}_{g2}", vtype="B")
                m.addConsIndicator(x[a, f] - x[b, g2] >= 1, binvar=g)
                wins.append(g)
        m.addCons(quicksum(wins) >= 19)

    # Output: the dice as a 5 x 6 list, row order Rock, Paper, Scissors, Lizard, Spock.
    dice = [[x[d, f] for f in range(FACES)] for d in range(5)]
    return m, {"dice": dice}
