# Big Bang nontransitive dice: choose five six-faced dice (Rock, Paper, Scissors,
# Lizard, Spock) so that each die beats exactly the two dice it beats in
# Rock-Paper-Scissors-Lizard-Spock.
import z3


def build(instance):
    del instance  # the puzzle states its own dice, faces and relations

    rock, paper, scissors, lizard, spock = range(5)

    m = 5   # number of dice
    n = 6   # faces on each die
    f = 12  # largest face value

    # Problem data: each pair (winner, loser) is one "beats" relationship of the game.
    edge = [
        (rock, scissors),   # Rock crushes Scissors
        (rock, lizard),     # Rock crushes Lizard
        (paper, rock),      # Paper covers Rock
        (paper, spock),     # Paper disproves Spock
        (scissors, paper),  # Scissors cuts Paper
        (scissors, lizard),  # Scissors decapitates Lizard
        (lizard, paper),    # Lizard eats Paper
        (lizard, spock),    # Lizard poisons Spock
        (spock, rock),      # Spock vaporizes Rock
        (spock, scissors),  # Spock smashes Scissors
    ]

    # dice[i][j] = value on face j of die i, between 1 and f (repeats are allowed).
    dice = [[z3.Int(f"dice_{i}_{j}") for j in range(n)] for i in range(m)]

    solver = z3.Solver()
    for die in dice:
        for face in die:
            solver.add(face >= 1, face <= f)

    # A beats B when A shows the strictly larger face in more than half of all
    # n*n face pairs. A pseudo-Boolean "at least" constraint over the pair
    # comparisons states this without integer sums.
    needed = (n * n) // 2 + 1
    for winner, loser in edge:
        wins = [(dice[winner][x] > dice[loser][y], 1) for x in range(n) for y in range(n)]
        solver.add(z3.PbGe(wins, needed))

    return solver, {"dice": dice}
