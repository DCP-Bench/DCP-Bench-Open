# Nontransitive dice (Rock-Paper-Scissors-Lizard-Spock): five six-faced dice with faces 1..12
# such that each die beats exactly the dice its choice beats in the game, where die A beats die B
# when A shows the larger face in more than half of all face pairs.
from pychoco.model import Model

# The puzzle has no instance data; the dice, faces and the game's ten 'beats' relations are its
# statement.
ROCK, PAPER, SCISSORS, LIZARD, SPOCK = range(5)
N_DICE = 5
N_FACES = 6
MAX_FACE = 12
BEATS = [
    (ROCK, SCISSORS),      # Rock crushes Scissors
    (ROCK, LIZARD),        # Rock crushes Lizard
    (PAPER, ROCK),         # Paper covers Rock
    (PAPER, SPOCK),        # Paper disproves Spock
    (SCISSORS, PAPER),     # Scissors cuts Paper
    (SCISSORS, LIZARD),    # Scissors decapitates Lizard
    (LIZARD, PAPER),       # Lizard eats Paper
    (LIZARD, SPOCK),       # Lizard poisons Spock
    (SPOCK, ROCK),         # Spock vaporizes Rock
    (SPOCK, SCISSORS),     # Spock smashes Scissors
]


def build(instance):
    del instance  # the puzzle carries no instance data

    model = Model()

    # dice[i][j] = value of face j of die i; values may repeat within and across dice
    dice = [[model.intvar(1, MAX_FACE, name=f"dice_{i}_{j}") for j in range(N_FACES)]
            for i in range(N_DICE)]

    # For every 'beats' relation, the winner's face is strictly larger than the loser's face in
    # more than half of the N_FACES * N_FACES face pairs.
    for winner, loser in BEATS:
        wins = [model.arithm(dice[winner][a], ">", dice[loser][b]).reify()
                for a in range(N_FACES) for b in range(N_FACES)]
        model.sum(wins, ">", (N_FACES * N_FACES) // 2).post()

    return model, {"dice": dice}
