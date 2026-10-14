# Knight's tour: number the squares of an n x n board 0..n*n-1 so that a knight
# can walk through them in numerical order, moving from each square to the
# next with a knight's move. The tour does not have to return to its start.
import functools
import operator

from hermax.model import Model

# The eight moves of a knight. These belong to the rules of chess, not the instance.
KNIGHT_MOVES = [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)]


def exactly_one(m, lits, name):
    """Post "exactly one of lits is true" with a ladder encoding.

    prefix[i] says that one of lits[0..i] is true; each literal sets its prefix,
    prefixes carry on, and a literal after a set prefix is forbidden. That takes
    three clauses per literal, where forbidding every pair takes a quadratic number,
    which matters here because the vectors have one entry per square of the board.
    """
    prefix = m.bool_vector(name, len(lits))
    for i, lit in enumerate(lits):
        m &= (~lit | prefix[i])
        if i + 1 < len(lits):
            m &= (~prefix[i] | prefix[i + 1])
            m &= (~lits[i + 1] | ~prefix[i])
    m &= functools.reduce(operator.or_, lits)


def build(instance):
    n = instance["n"]  # board size
    squares = n * n  # numbers run from 0 to squares - 1

    # The squares a knight can reach from square s = i * n + j in one move.
    def moves(s):
        i, j = divmod(s, n)
        return [(i + di) * n + (j + dj) for di, dj in KNIGHT_MOVES
                if 0 <= i + di < n and 0 <= j + dj < n]

    m = Model()
    # x[i][j] = the move number at which the knight is on square (i, j) (the declared output)
    x = m.int_matrix("x", n, n, 0, squares - 1)
    # holds[s][k] = square s has move number k (one-hot form of x)
    holds = [m.bool_vector(f"holds_{s}", squares) for s in range(squares)]

    # every square is visited at exactly one move number, and every move number is used once
    for s in range(squares):
        exactly_one(m, [holds[s][k] for k in range(squares)], f"square_{s}")
        exactly_one(m, [holds[t][s] for t in range(squares)], f"number_{s}")
    # x shows the move number held: holding k means x >= k and not x >= k + 1 (the
    # comparison that would fall outside the range of x is already settled)
    for i in range(n):
        for j in range(n):
            for k in range(squares):
                if k > 0:
                    m &= (~holds[i * n + j][k] | (x[i][j] >= k))
                if k < squares - 1:
                    m &= (~holds[i * n + j][k] | ~(x[i][j] >= k + 1))

    # step[(s, t)] = the knight moves from square s straight to square t. This
    # restates the tour as a path on the knight's graph, which lets the solver
    # see at once that a square with few moves (a corner) has them all on the path.
    step = {(s, t): m.bool(f"step_{s}_{t}") for s in range(squares) for t in moves(s)}
    for s in range(squares):
        out_steps = [step[(s, t)] for t in moves(s)]
        in_steps = [step[(t, s)] for t in moves(s)]
        # Every square but the last has exactly one step out of it, and every
        # square but the first has exactly one step into it.
        m &= (sum(out_steps + [holds[s][squares - 1]]) == 1)
        m &= (sum(in_steps + [holds[s][0]]) == 1)
        for t in moves(s):
            for k in range(squares - 1):
                # a step from s to t takes the number from k to k + 1, and back
                m &= (~step[(s, t)] | ~holds[s][k] | holds[t][k + 1])
                m &= (~step[(s, t)] | ~holds[t][k + 1] | holds[s][k])

    # The knight moves from one numbered square to the next: if a square has
    # number k, a knight's move away there is a square with number k + 1, and
    # (for k > 0) one with number k - 1. Each number is used once, so that
    # square is unique.
    for s in range(squares):
        reach = moves(s)
        for k in range(squares):
            if k < squares - 1:
                m &= (~holds[s][k] | functools.reduce(operator.or_, [holds[t][k + 1] for t in reach]))
            if k > 0:
                m &= (~holds[s][k] | functools.reduce(operator.or_, [holds[t][k - 1] for t in reach]))

    return m, {"x": x}
