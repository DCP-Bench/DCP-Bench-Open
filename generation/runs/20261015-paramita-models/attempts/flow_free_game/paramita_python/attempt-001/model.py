# Flow Free: connect the two cells of each colour with a pipe, so that the
# pipes do not cross or overlap and together cover the entire board. Print the
# colour of every cell as an integer.
from paramita.modelling import Bool, If, Iff, Or


def build(instance):
    board = instance["board"]  # the given board, read from the instance
    n = len(board)
    m = len(board[0])
    cells = [(i, j) for i in range(n) for j in range(m)]
    colours = sorted({v for row in board for v in row if v > 0})
    max_level = n * m - 1  # a pipe covers at most every cell

    def nbrs(p):
        i, j = p
        out = []
        for di, dj in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            if 0 <= i + di < n and 0 <= j + dj < m:
                out.append((i + di, j + dj))
        return out

    # the given endpoint cells of each colour, in board order
    ends = {c: [(i, j) for (i, j) in cells if board[i][j] == c] for c in colours}

    # L[(c, p, d)] = cell p is on the pipe of colour c at distance d from the first endpoint of c
    L = {(c, p, d): Bool(f"lev_{c}_{p[0]}_{p[1]}_{d}") for c in colours for p in cells for d in range(max_level + 1)}
    # col[(c, p)] = cell p carries colour c
    col = {(c, p): Bool(f"col_{c}_{p[0]}_{p[1]}") for c in colours for p in cells}

    cons = []

    # every cell is covered by exactly one pipe, so one colour and one distance
    for p in cells:
        cons.append(sum(L[(c, p, d)] for c in colours for d in range(max_level + 1)) == 1)

    # col is true exactly when the cell carries that colour
    for c in colours:
        for p in cells:
            cons.append(Iff(col[(c, p)], Or([L[(c, p, d)] for d in range(max_level + 1)])))

    # the given cells keep their colour
    for c in colours:
        for p in ends[c]:
            cons.append(col[(c, p)])

    # the first endpoint of each colour starts its pipe at distance 0, and no other cell is at distance 0
    for c in colours:
        a_cell = ends[c][0]
        cons.append(L[(c, a_cell, 0)])
        for p in cells:
            if p != a_cell:
                cons.append(~L[(c, p, 0)])

    # a pipe cell at distance d is next to a pipe cell of the same colour at distance d - 1,
    # so every pipe is connected to its first endpoint and contains no separate loop
    for c in colours:
        for p in cells:
            for d in range(1, max_level + 1):
                cons.append(~L[(c, p, d)] | Or([L[(c, q, d - 1)] for q in nbrs(p)]))

    # a pipe does not cross or overlap itself: each pipe cell touches exactly two cells of its colour,
    # and each endpoint touches exactly one
    for c in colours:
        for p in cells:
            same = sum(col[(c, q)] for q in nbrs(p))
            if p in ends[c]:
                cons.append(If(col[(c, p)], same == 1))
            else:
                cons.append(If(col[(c, p)], same == 2))

    # the colour of each cell as an integer
    B = [[sum(c * col[(c, (i, j))] for c in colours) for j in range(m)] for i in range(n)]
    return cons, {"B": B}
