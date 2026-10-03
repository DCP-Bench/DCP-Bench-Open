"""Nontransitive dice (Rock-Paper-Scissors-Lizard-Spock): five six-sided dice with faces
1..12 such that each of the ten 'beats' relations of the game holds, where die A beats
die B when A shows the strictly larger face in more than half of the 36 face pairs.

The model reports the dice, one row per die: Rock, Paper, Scissors, Lizard, Spock.
"""
import pulp


def build(instance):
    del instance  # the puzzle has no instance data; its constants are below

    # Problem constants, mirrored from the reference.
    rock, paper, scissors, lizard, spock = range(5)
    m = 5   # number of dice
    n = 6   # faces per die
    f = 12  # largest face value
    edge = [
        [rock, scissors],   # Rock crushes Scissors
        [rock, lizard],     # Rock crushes Lizard
        [paper, rock],      # Paper covers Rock
        [paper, spock],     # Paper disproves Spock
        [scissors, paper],  # Scissors cuts Paper
        [scissors, lizard],  # Scissors decapitates Lizard
        [lizard, paper],    # Lizard eats Paper
        [lizard, spock],    # Lizard poisons Spock
        [spock, rock],      # Spock vaporizes Rock
        [spock, scissors],  # Spock smashes Scissors
    ]

    problem = pulp.LpProblem("big_bang2", pulp.LpMinimize)  # satisfaction

    # dice[i][j] is the value of face j of die i; values may repeat
    dice = [[pulp.LpVariable(f"dice_{i}_{j}", 1, f, cat="Integer") for j in range(n)]
            for i in range(m)]

    # For each relation 'winner beats loser', wins[x, y] = 1 may only be set when face x of
    # the winner is strictly larger than face y of the loser. Only this direction is
    # needed: the count of wins must be large, so the solver never benefits from leaving a
    # true win at 0. The big-M f is the largest face difference plus one.
    for winner, loser in edge:
        wins = []
        for x in range(n):
            for y in range(n):
                win = pulp.LpVariable(f"win_{winner}_{loser}_{x}_{y}", cat="Binary")
                problem += dice[winner][x] - dice[loser][y] >= 1 - f * (1 - win)
                wins.append(win)
        # the winner shows the larger face in more than half of all face pairs
        problem += pulp.lpSum(wins) >= (n * n) // 2 + 1

    return problem, {"dice": dice}
