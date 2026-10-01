# Non-transitive dice for Rock-Paper-Scissors-Lizard-Spock: design five six-sided dice with
# faces 1..12 so that each die beats exactly the two dice it beats in the game. Die A beats die B
# when, over all 36 pairs of faces, A shows the strictly larger value in more than half of them.
import cpmpy as cp


def build(instance):
    # The instance carries no data: the game and the dice are fixed by the problem itself.
    rock, paper, scissors, lizard, spock = 0, 1, 2, 3, 4
    n_dice = 5       # one die per choice (problem constant)
    n_faces = 6      # faces per die (problem constant)
    max_face = 12    # faces carry values 1..12 (problem constant)

    # (winner, loser) for the ten relationships of the game (problem constants)
    beats = [
        (rock, scissors),      # rock crushes scissors
        (rock, lizard),        # rock crushes lizard
        (paper, rock),         # paper covers rock
        (paper, spock),        # paper disproves Spock
        (scissors, paper),     # scissors cuts paper
        (scissors, lizard),    # scissors decapitates lizard
        (lizard, paper),       # lizard eats paper
        (lizard, spock),       # lizard poisons Spock
        (spock, rock),         # Spock vaporizes rock
        (spock, scissors),     # Spock smashes scissors
    ]

    # dice[i, j] = value on face j of die i (row 0 rock, 1 paper, 2 scissors, 3 lizard, 4 Spock);
    # values may repeat within a die and across dice
    dice = cp.intvar(1, max_face, shape=(n_dice, n_faces), name="dice")

    model = cp.Model()

    # A winning die beats the losing die: among all n_faces * n_faces pairs of faces, the winner
    # shows the strictly larger value in more than half of the pairs.
    for winner, loser in beats:
        wins = [dice[winner, x] > dice[loser, y] for x in range(n_faces) for y in range(n_faces)]
        model += cp.sum(wins) > (n_faces * n_faces) // 2

    return model, {"dice": dice}
