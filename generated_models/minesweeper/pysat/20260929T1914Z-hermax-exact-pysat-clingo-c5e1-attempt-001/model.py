# Minesweeper: from the revealed numbers of a board, decide which of the
# unopened cells hold a mine. An opened cell is safe and shows how many of its
# (up to eight) neighbours are mines.
from pysat.card import CardEnc, EncType
from pysat.formula import CNF, IDPool


def build(instance):
    unopened = instance["X"]  # the value that marks a cell that is not opened
    game = instance["game_data"]
    rows, cols = len(game), len(game[0])

    pool = IDPool()
    # mines[r][c] is true when cell (r, c) holds a mine
    mines = [[pool.id(("mine", r, c)) for c in range(cols)] for r in range(rows)]

    cnf = CNF()
    for r in range(rows):
        for c in range(cols):
            if game[r][c] != unopened:
                # an opened cell is not a mine
                cnf.append([-mines[r][c]])
                # its number is the count of mines among its neighbours
                around = [mines[a][b]
                          for a in range(max(0, r - 1), min(rows, r + 2))
                          for b in range(max(0, c - 1), min(cols, c + 2))
                          if (a, b) != (r, c)]
                cnf.extend(CardEnc.equals(lits=around, bound=game[r][c], vpool=pool,
                                          encoding=EncType.seqcounter).clauses)

    return cnf, {"mines": mines}
