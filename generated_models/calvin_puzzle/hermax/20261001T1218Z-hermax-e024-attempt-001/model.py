# Calvin puzzle: number the n by n squares of a grid 1..n*n, each number once, so that
# every number is followed by the next one a fixed distance away: three squares away
# horizontally or vertically (a gap of two squares between them), or two squares away
# in both directions diagonally (a gap of one square between them). The numbers can
# start anywhere.
import functools
import operator

from hermax.model import Model

# The moves from one number to the next, as (row step, column step). These belong to the
# rules of the puzzle, not to the instance: three squares straight, two squares diagonally.
MOVES = [(3, 0), (-3, 0), (0, 3), (0, -3), (2, 2), (2, -2), (-2, 2), (-2, -2)]


def exactly_one(m, lits, name):
    """Post "exactly one of lits is true" with a ladder encoding.

    prefix[i] says that one of lits[0..i] is true; each literal sets its prefix,
    prefixes carry on, and a literal after a set prefix is forbidden. That takes
    three clauses per literal, where forbidding every pair takes a quadratic number,
    which matters here because the vectors have one entry per square of the grid.
    """
    prefix = m.bool_vector(name, len(lits))
    for i, lit in enumerate(lits):
        m &= (~lit | prefix[i])
        if i + 1 < len(lits):
            m &= (~prefix[i] | prefix[i + 1])
            m &= (~lits[i + 1] | ~prefix[i])
    m &= functools.reduce(operator.or_, lits)


def build(instance):
    n = instance["n"]  # side of the grid
    squares = n * n  # the numbers are 1..squares

    # The squares reachable from square s = i * n + j by one move of the puzzle.
    def moves(s):
        i, j = divmod(s, n)
        return [(i + di) * n + (j + dj) for di, dj in MOVES
                if 0 <= i + di < n and 0 <= j + dj < n]

    m = Model()
    # x[i][j] = the number written in square (i, j) (the declared output)
    x = m.int_matrix("x", n, n, 1, squares)
    # holds[s][k] = square s holds the number k + 1 (the one-hot form of x)
    holds = [m.bool_vector(f"holds_{s}", squares) for s in range(squares)]

    # every square holds exactly one number and every number is written in one square
    # (the numbers are all different)
    for s in range(squares):
        exactly_one(m, [holds[s][k] for k in range(squares)], f"square_{s}")
        exactly_one(m, [holds[t][s] for t in range(squares)], f"number_{s}")
    # x shows the number held: holding k + 1 means x >= k + 1 and not x >= k + 2 (the
    # comparison that would fall outside the range of x is already settled)
    for i in range(n):
        for j in range(n):
            for k in range(squares):
                if k > 0:
                    m &= (~holds[i * n + j][k] | (x[i][j] >= k + 1))
                if k < squares - 1:
                    m &= (~holds[i * n + j][k] | ~(x[i][j] >= k + 2))

    # step[(s, t)] = the number after the one in square s is in square t. This restates
    # the numbering as a path through the squares, which lets the solver see at once that
    # a square with few possible moves has them all on the path.
    step = {(s, t): m.bool(f"step_{s}_{t}") for s in range(squares) for t in moves(s)}
    for s in range(squares):
        out_steps = [step[(s, t)] for t in moves(s)]
        in_steps = [step[(t, s)] for t in moves(s)]
        # every square but the one with the last number has exactly one step out of it,
        # and every square but the one with number 1 has exactly one step into it
        m &= (sum(out_steps + [holds[s][squares - 1]]) == 1)
        m &= (sum(in_steps + [holds[s][0]]) == 1)
        for t in moves(s):
            for k in range(squares - 1):
                # a step from s to t takes the number from k + 1 to k + 2, and back
                m &= (~step[(s, t)] | ~holds[s][k] | holds[t][k + 1])
                m &= (~step[(s, t)] | ~holds[t][k + 1] | holds[s][k])

    # Every number but the last is followed by the next one a move away, and every number
    # but the first is preceded by the previous one a move away. Each number is written
    # once, so that square is unique.
    for s in range(squares):
        reach = moves(s)
        for k in range(squares):
            if k < squares - 1:
                if reach:
                    m &= (~holds[s][k] | functools.reduce(operator.or_, [holds[t][k + 1] for t in reach]))
                else:  # no move leaves this square, so it can only hold the last number
                    m &= ~holds[s][k]
            if k > 0:
                if reach:
                    m &= (~holds[s][k] | functools.reduce(operator.or_, [holds[t][k - 1] for t in reach]))
                else:  # no move enters this square, so it can only hold the first number
                    m &= ~holds[s][k]

    return m, {"x": x}
