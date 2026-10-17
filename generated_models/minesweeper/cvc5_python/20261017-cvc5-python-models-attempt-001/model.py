# Minesweeper: determine which unopened cells contain mines, from the revealed clue numbers.
# Each cell is a Boolean (True = mine). Board size and clues come from the instance.
import cvc5.pythonic as cz


def build(instance):
    grid = instance["game_data"]
    unknown = instance["X"]
    rows = len(grid)
    cols = len(grid[0])

    mines = [[cz.Bool(f"m_{i}_{j}") for j in range(cols)] for i in range(rows)]
    constraints = []

    # The number on a cell shows the number of mines adjacent to it.
    # Opened cells (clue numbers) are safe, so they contain no mine.
    for i in range(rows):
        for j in range(cols):
            clue = grid[i][j]
            if clue == unknown:
                continue
            constraints.append(cz.Not(mines[i][j]))
            neighbours = [
                mines[a][b]
                for a in range(max(0, i - 1), min(rows, i + 2))
                for b in range(max(0, j - 1), min(cols, j + 2))
                if (a, b) != (i, j)
            ]
            if neighbours:
                constraints.append(
                    cz.Sum([cz.If(m, 1, 0) for m in neighbours]) == clue
                )

    return constraints, {"mines": mines}
