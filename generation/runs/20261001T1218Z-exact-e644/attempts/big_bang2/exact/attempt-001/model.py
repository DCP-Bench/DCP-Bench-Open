# Big Bang nontransitive dice: build five six-faced dice with face values 1..12 so that their
# "beats" relation matches Rock-Paper-Scissors-Lizard-Spock. Die A beats die B when A shows a
# strictly larger face than B in more than half of all pairs of faces.
from exact import Exact


def build(instance):
    # This problem has no instance data. The numbers of dice, faces and values and the ten
    # "beats" relations belong to the problem statement.
    rock, paper, scissors, lizard, spock = range(5)
    m = 5  # number of dice
    n = 6  # number of faces of each die
    f = 12  # largest face value
    edge = [
        (rock, scissors),  # Rock crushes Scissors
        (rock, lizard),  # Rock crushes Lizard
        (paper, rock),  # Paper covers Rock
        (paper, spock),  # Paper disproves Spock
        (scissors, paper),  # Scissors cut Paper
        (scissors, lizard),  # Scissors decapitate Lizard
        (lizard, paper),  # Lizard eats Paper
        (lizard, spock),  # Lizard poisons Spock
        (spock, rock),  # Spock vaporizes Rock
        (spock, scissors),  # Spock smashes Scissors
    ]

    solver = Exact()

    # dice[i][j] = value of the j-th face of die i, between 1 and f
    dice = [[f"dice_{i}_{j}" for j in range(n)] for i in range(m)]
    for i in range(m):
        for j in range(n):
            solver.addVariable(dice[i][j], 1, f)

    # The faces of each die are listed in non-decreasing order. This only removes reorderings of
    # the same die; the declared output (dice) is unchanged and any face order is a valid answer.
    for i in range(m):
        for j in range(n - 1):
            solver.addConstraint([(1, dice[i][j]), (-1, dice[i][j + 1])], False, 0, True, 0)

    # For every "beats" relation the number of pairs of faces where the winner shows a strictly
    # larger value than the loser has to be more than half of all pairs. wins[w][l][x][y] can be 1
    # only if face x of die w is larger than face y of die l: the big-M term (f) relaxes
    # dice[w][x] - dice[l][y] >= 1 when it is 0.
    for winner, loser in edge:
        pairs = []
        for x in range(n):
            for y in range(n):
                wins = f"wins_{winner}_{loser}_{x}_{y}"
                solver.addVariable(wins, 0, 1)
                solver.addConstraint([(1, dice[winner][x]), (-1, dice[loser][y]), (-f, wins)],
                                     True, 1 - f)
                pairs.append((1, wins))
        # more than half of the n * n pairs
        solver.addConstraint(pairs, True, (n * n) // 2 + 1)
        # Because both dice are sorted, a pair won by a face is also won by every larger face of
        # the winner and every smaller face of the loser (implied; it helps the search).
        for x in range(n):
            for y in range(n):
                if x + 1 < n:
                    solver.addConstraint([(1, f"wins_{winner}_{loser}_{x}_{y}"),
                                          (-1, f"wins_{winner}_{loser}_{x + 1}_{y}")],
                                         False, 0, True, 0)
                if y > 0:
                    solver.addConstraint([(1, f"wins_{winner}_{loser}_{x}_{y}"),
                                          (-1, f"wins_{winner}_{loser}_{x}_{y - 1}")],
                                         False, 0, True, 0)

    return solver, {"dice": dice}
