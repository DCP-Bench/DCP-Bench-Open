# Big bang (nontransitive dice): five six-faced dice with faces 1 to 12 whose "beats"
# relation is that of Rock-Paper-Scissors-Lizard-Spock. Die A beats die B when A shows the
# larger face in more than half of the 36 pairs of faces.
from hermax.model import Model

# The game is fixed by the problem; the instance carries no data.
ROCK, PAPER, SCISSORS, LIZARD, SPOCK = range(5)
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
    dice_count = 5   # one die per choice
    faces = 6        # faces per die
    top = 12         # largest face value

    m = Model()
    # dice[i][j] = the value on face j of die i (row 0 Rock, 1 Paper, 2 Scissors, 3 Lizard, 4 Spock)
    dice = m.int_matrix("dice", dice_count, faces, 1, top)

    for winner, loser in BEATS:
        # wins[x][y] may only be true when face x of the winner is larger than face y of
        # the loser: if the loser's face is at least v, the winner's face is at least v + 1.
        # Only this direction is needed, since the count below is a lower bound.
        wins = m.bool_matrix(f"wins_{winner}_{loser}", faces, faces)
        for x in range(faces):
            for y in range(faces):
                w, lo = dice[winner][x], dice[loser][y]
                m &= (~wins[x][y] | ~(lo >= top))
                for v in range(2, top):
                    m &= (~wins[x][y] | ~(lo >= v) | (w >= v + 1))
                m &= (~wins[x][y] | (w >= 2))
        # the winner shows the larger face in more than half of the 36 pairs
        m &= (sum(wins.flatten()) >= faces * faces // 2 + 1)

    return m, {"dice": dice}
