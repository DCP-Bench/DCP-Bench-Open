# Knight's tour on an n x n chessboard (n from the instance), using Python-MIP with CBC.
# A knight's tour is a sequence of moves of a knight on a chessboard such that the knight visits every
# square exactly once (without returning to the starting square).
# The tour is represented by integers from 0 to n*n-1, where n is the size of the chessboard.
# Output x[i][j] is the move number of the knight on square (i, j).
import mip


KNIGHT_MOVES = [(1, 2), (2, 1), (2, -1), (1, -2), (-1, -2), (-2, -1), (-2, 1), (-1, 2)]


def build(instance):
    n = instance["n"]
    total = n * n
    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    squares = [(i, j) for i in range(n) for j in range(n)]

    def neighbours(i, j):
        result = []
        for di, dj in KNIGHT_MOVES:
            a, b = i + di, j + dj
            if 0 <= a < n and 0 <= b < n:
                result.append((a, b))
        return result

    # arc[(s, q)] = 1 when the knight moves from square s directly to the square q
    arc = {}
    for (i, j) in squares:
        for (a, b) in neighbours(i, j):
            arc[((i, j), (a, b))] = model.add_var(f"arc_{i}_{j}_{a}_{b}", var_type=mip.BINARY)

    # x[i][j] is the move number of square (i, j)
    x = {(i, j): model.add_var(f"x_{i}_{j}", lb=0, ub=total - 1, var_type=mip.INTEGER)
         for (i, j) in squares}

    # Each square is left at most once and entered at most once.
    for (i, j) in squares:
        model.add_constr(mip.xsum(arc[((i, j), q)] for q in neighbours(i, j)) <= 1)
        incoming = [arc[(s, (i, j))] for s in neighbours(i, j)]
        model.add_constr(mip.xsum(incoming) <= 1)

    # The knight visits every square exactly once: the moves form one path through all squares.
    model.add_constr(mip.xsum(arc.values()) == total - 1)

    # Move numbers increase by one along each move, so the path has no cycle.
    # Big-M is total: the largest move number minus the smallest, plus one.
    big_m = total
    for (s, q), var in arc.items():
        model.add_constr(x[q] >= x[s] + 1 - big_m * (1 - var))

    # The output is the move number of each square, as a list of lists.
    outputs = {"x": [[x[(i, j)] for j in range(n)] for i in range(n)]}
    model.verbose = 0
    model.threads = 1
    model.max_mip_gap = 0.0
    model.max_mip_gap_abs = 0.0
    return model, outputs
