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

    # at_least[i][j][v] = 1 if face j of die i shows v or more (order encoding). The value
    # 1 is always reached and f + 1 never, so those two levels are constants. A face
    # value is 1 plus the number of levels 2..f it reaches. Values may repeat.
    def at_least(i, j, v):
        if v <= 1:
            return 1
        if v > f:
            return 0
        return level[i][j][v]

    level = [[{v: pulp.LpVariable(f"atleast_{i}_{j}_{v}", cat="Binary") for v in range(2, f + 1)}
              for j in range(n)] for i in range(m)]
    for i in range(m):
        for j in range(n):
            for v in range(3, f + 1):
                problem += level[i][j][v] <= level[i][j][v - 1]
    dice = [[1 + pulp.lpSum(level[i][j].values()) for j in range(n)] for i in range(m)]

    # For each relation 'winner beats loser', win[x, y] = 1 may only be set when face x of
    # the winner is strictly larger than face y of the loser: whenever the loser's face
    # reaches v, the winner's face reaches v + 1. Stated level by level this is much
    # tighter than one big-M comparison of the two values.
    for winner, loser in edge:
        wins = []
        for x in range(n):
            for y in range(n):
                win = pulp.LpVariable(f"win_{winner}_{loser}_{x}_{y}", cat="Binary")
                for v in range(1, f + 1):
                    problem += win <= 1 - at_least(loser, y, v) + at_least(winner, x, v + 1)
                wins.append(win)
        # the winner shows the larger face in more than half of all face pairs
        problem += pulp.lpSum(wins) >= (n * n) // 2 + 1

    return problem, {"dice": dice}
