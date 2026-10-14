# Flow Free: a board has some cells with a colour (the ends of the pipes) and some empty cells.
# Fill every cell with a colour so that each given cell touches exactly one cell of its own
# colour and each empty cell touches exactly two cells of its own colour, i.e. every colour
# forms pipes that run through the board without crossing.
from pysat.card import CardEnc, EncType
from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def build(instance):
    board = instance["board"]  # board[i][j] = colour of a given cell, 0 for an empty cell
    rows, cols = len(board), len(board[0])
    n_colors = 10  # a cell takes a colour 1..10 (the reference allows more colours than the board uses)

    pool = IDPool()
    # B[i][j] = the colour of the cell in row i and column j
    B = [[Integer(f"B{i}_{j}", 1, n_colors, vpool=pool) for j in range(cols)] for i in range(rows)]
    engine = IntegerEngine(vars=[cell for row in B for cell in row], vpool=pool)
    cnf = engine.clausify()

    cells = [(i, j) for i in range(rows) for j in range(cols)]

    def neighbours(i, j):
        return [(k, l) for (k, l) in cells if abs(k - i) + abs(l - j) == 1]

    # same[(p, q)] = a literal that is true exactly when the cells p and q (side by side) have the
    # same colour; it is shared by the two cells it concerns
    same = {}

    def same_colour(p, q):
        key = (min(p, q), max(p, q))
        if key not in same:
            literal = pool.id(("same", key))
            x, y = B[key[0][0]][key[0][1]], B[key[1][0]][key[1][1]]
            for color in range(1, n_colors + 1):
                cnf.append([-x.equals(color), -y.equals(color), literal])
                for other in range(1, n_colors + 1):
                    if other != color:
                        cnf.append([-literal, -x.equals(color), -y.equals(other)])
            same[key] = literal
        return same[key]

    for i, j in cells:
        touching = [same_colour((i, j), q) for q in neighbours(i, j)]
        if board[i][j] != 0:
            # a given cell keeps its colour and touches exactly one cell of that colour (the next
            # cell of its pipe)
            cnf.append([B[i][j].equals(board[i][j])])
            cnf.extend(CardEnc.equals(lits=touching, bound=1, vpool=pool,
                                      encoding=EncType.seqcounter).clauses)
        else:
            # an empty cell is filled with a pipe cell that touches exactly two cells of its own
            # colour (the previous and the next cell of its pipe)
            cnf.extend(CardEnc.equals(lits=touching, bound=2, vpool=pool,
                                      encoding=EncType.seqcounter).clauses)

    return cnf, {"B": B}
