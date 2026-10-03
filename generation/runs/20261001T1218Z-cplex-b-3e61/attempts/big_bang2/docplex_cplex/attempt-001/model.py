"""Nontransitive dice for Rock-Paper-Scissors-Lizard-Spock: five six-faced dice with faces 1..12
whose "beats" relation (a die beats another when its face is strictly larger in more than half of
the 36 face pairs) matches the ten "beats" relations of the game.

The model reports the faces of each die (Rock, Paper, Scissors, Lizard, Spock). The puzzle has no
instance data; the dice sizes and the relations are the puzzle's own.
"""
from docplex.mp.model import Model


def build(instance):
    rock, paper, scissors, lizard, spock = range(5)
    m = 5   # number of dice (puzzle constant)
    n = 6   # faces per die (puzzle constant)
    f = 12  # largest face value (puzzle constant)
    # Who beats whom in the game (puzzle constant).
    edge = [
        [rock, scissors],     # Rock crushes Scissors
        [rock, lizard],       # Rock crushes Lizard
        [paper, rock],        # Paper covers Rock
        [paper, spock],       # Paper disproves Spock
        [scissors, paper],    # Scissors cuts Paper
        [scissors, lizard],   # Scissors decapitates Lizard
        [lizard, paper],      # Lizard eats Paper
        [lizard, spock],      # Lizard poisons Spock
        [spock, rock],        # Spock vaporizes Rock
        [spock, scissors],    # Spock smashes Scissors
    ]
    faces = range(n)

    model = Model("big_bang2")

    # dice[i][j] is the value of face j of die i; faces may repeat within and across dice.
    dice = [[model.integer_var(1, f, name=f"dice_{i}_{j}") for j in faces] for i in range(m)]

    # A winner beats a loser when its face is strictly larger in more than half of the face
    # pairs. wins[x, y] = 1 can only be claimed for a pair where the winner's face x is larger
    # than the loser's face y; more than n*n/2 pairs must be claimed.
    for winner, loser in edge:
        claimed = []
        for x in faces:
            for y in faces:
                w = model.binary_var(name=f"wins_{winner}_{loser}_{x}_{y}")
                model.add_indicator(w, dice[winner][x] >= dice[loser][y] + 1)
                claimed.append(w)
        model.add_constraint(model.sum(claimed) >= (n * n) // 2 + 1)

    return model, {"dice": dice}
