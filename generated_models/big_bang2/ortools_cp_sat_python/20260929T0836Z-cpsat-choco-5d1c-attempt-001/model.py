# Big Bang nontransitive dice: build five dice (Rock, Paper, Scissors, Lizard,
# Spock), each with six faces of value 1..12, so that the "beats" relation
# between the dice is exactly that of the game Rock-Paper-Scissors-Lizard-Spock.
# Die A beats die B when A shows the larger face in more than half of all pairs of faces.
from ortools.sat.python import cp_model

# The instance has no data: the game itself fixes these constants.
ROCK, PAPER, SCISSORS, LIZARD, SPOCK = range(5)
N_DICE = 5
N_FACES = 6
MAX_FACE = 12
# (winner, loser) for the ten rules of the game
BEATS = [
    (ROCK, SCISSORS),  # rock crushes scissors
    (ROCK, LIZARD),  # rock crushes lizard
    (PAPER, ROCK),  # paper covers rock
    (PAPER, SPOCK),  # paper disproves Spock
    (SCISSORS, PAPER),  # scissors cut paper
    (SCISSORS, LIZARD),  # scissors decapitate lizard
    (LIZARD, PAPER),  # lizard eats paper
    (LIZARD, SPOCK),  # lizard poisons Spock
    (SPOCK, ROCK),  # Spock vaporizes rock
    (SPOCK, SCISSORS),  # Spock smashes scissors
]


def build(instance):
    model = cp_model.CpModel()

    # dice[i][j] = the value on the j-th face of die i
    dice = [[model.new_int_var(1, MAX_FACE, f"dice_{i}_{j}") for j in range(N_FACES)] for i in range(N_DICE)]

    for winner, loser in BEATS:
        # count the face pairs (x, y) where the winner's face is larger than the loser's
        wins = []
        for x in range(N_FACES):
            for y in range(N_FACES):
                bigger = model.new_bool_var(f"bigger_{winner}_{x}_{loser}_{y}")
                model.add(dice[winner][x] > dice[loser][y]).only_enforce_if(bigger)
                model.add(dice[winner][x] <= dice[loser][y]).only_enforce_if(bigger.negated())
                wins.append(bigger)
        # the winner must win in more than half of all face pairs
        model.add(sum(wins) > (N_FACES * N_FACES) // 2)

    return model, {"dice": dice}
