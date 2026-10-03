"""Nontransitive dice: five six-faced dice (faces 1..12) whose 'beats' relation is that of Rock-Paper-Scissors-Lizard-Spock."""
import gurobipy as gp
from gurobipy import GRB


def build(instance):
    # The puzzle has no instance data: the dice count, faces, face range and the ten
    # 'beats' relations are the puzzle's own, mirrored from the reference.
    rock, paper, scissors, lizard, spock = range(5)
    m, n, f = 5, 6, 12      # dice, faces per die, largest face value
    edge = [
        (rock, scissors), (rock, lizard),
        (paper, rock), (paper, spock),
        (scissors, paper), (scissors, lizard),
        (lizard, paper), (lizard, spock),
        (spock, rock), (spock, scissors),
    ]
    faces = range(n)

    model = gp.Model("big_bang2")

    # dice[i, j]: value of face j of die i, from 1 to 12; values may repeat.
    dice = model.addVars(m, n, lb=1, ub=f, vtype=GRB.INTEGER, name="dice")

    # A die beats another when its face is strictly larger in more than half of the
    # n * n face pairs. higher[w, l, x, y] is 1 only if face x of the winner is larger
    # than face y of the loser, and more than half of these must be 1.
    for (w, l) in edge:
        higher = model.addVars(faces, faces, vtype=GRB.BINARY, name=f"higher[{w},{l}]")
        for x in faces:
            for y in faces:
                model.addConstr((higher[x, y] == 1) >> (dice[w, x] >= dice[l, y] + 1))
        model.addConstr(higher.sum() >= (n * n) // 2 + 1, name=f"beats[{w},{l}]")

    return model, {"dice": [[dice[i, j] for j in faces] for i in range(m)]}
