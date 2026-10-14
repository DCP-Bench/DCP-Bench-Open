# Flow Free: a board has some cells already holding a colour (the pipe ends) and empty cells. Colour
# every cell so that pipes of one colour form paths: an end cell touches exactly one cell of its
# colour, any other cell touches exactly two cells of its colour.
from exact import Exact


def build(instance):
    board = instance["board"]  # board[i][j] is the colour at row i, column j, or 0 when empty
    rows, cols = len(board), len(board[0])
    colours = range(1, 11)  # the reference lets every cell take a colour from 1 to 10

    solver = Exact()

    # B[i][j] is the colour of the cell; is_colour[i][j][c] = 1 when the cell has colour c.
    B = [[f"B_{i}_{j}" for j in range(cols)] for i in range(rows)]
    is_colour = [[{c: f"B_{i}_{j}_is_{c}" for c in colours} for j in range(cols)]
                 for i in range(rows)]
    for i in range(rows):
        for j in range(cols):
            solver.addVariable(B[i][j], 1, 10)
            for c in colours:
                solver.addVariable(is_colour[i][j][c], 0, 1)
            # the cell has exactly one colour, and the indicators give its value
            solver.addConstraint([(1, is_colour[i][j][c]) for c in colours], True, 1, True, 1)
            solver.addConstraint([(c, is_colour[i][j][c]) for c in colours] + [(-1, B[i][j])],
                                 True, 0, True, 0)
            # a cell that starts with a colour keeps it
            if board[i][j] != 0:
                solver.addConstraint([(1, is_colour[i][j][board[i][j]])], True, 1, True, 1)

    # same[(cell, neighbour)] = 1 exactly when two neighbouring cells have the same colour. For each
    # colour, both cells having it forces the variable up, and only one of them having it forces
    # it down.
    same = {}
    for i in range(rows):
        for j in range(cols):
            for k, l in ((i + 1, j), (i, j + 1)):
                if k < rows and l < cols:
                    name = f"same_{i}_{j}_{k}_{l}"
                    solver.addVariable(name, 0, 1)
                    for c in colours:
                        here, there = is_colour[i][j][c], is_colour[k][l][c]
                        solver.addConstraint([(1, name), (-1, here), (-1, there)], True, -1)
                        solver.addConstraint([(1, name), (1, here), (-1, there)], False, 0, True, 1)
                        solver.addConstraint([(1, name), (-1, here), (1, there)], False, 0, True, 1)
                    same[(i, j, k, l)] = name
                    same[(k, l, i, j)] = name

    # The number of neighbours with the same colour: exactly 1 for a cell that starts with a
    # colour (a pipe end), exactly 2 for an empty cell. The reference also allows colour 0 for an
    # empty cell, but 0 is outside the colour range 1..10, so that alternative never applies.
    for i in range(rows):
        for j in range(cols):
            neighbours = [(k, l) for k, l in ((i - 1, j), (i + 1, j), (i, j - 1), (i, j + 1))
                          if 0 <= k < rows and 0 <= l < cols]
            wanted = 1 if board[i][j] != 0 else 2
            solver.addConstraint([(1, same[(i, j, k, l)]) for k, l in neighbours],
                                 True, wanted, True, wanted)

    return solver, {"B": B}
