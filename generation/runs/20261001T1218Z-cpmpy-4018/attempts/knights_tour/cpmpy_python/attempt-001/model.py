# Knight's tour: number the squares of an n x n board 0..n*n-1 so that consecutive numbers are
# a knight's move apart, i.e. the knight visits every square exactly once (an open tour, any start).
import cpmpy as cp


def build(instance):
    n = instance["n"]
    cells = n * n

    # x[i, j] = the move at which the knight visits square (i, j), from 0 to n*n-1
    x = cp.intvar(0, cells - 1, shape=(n, n), name="x")

    # The legal knight's moves (a fixed fact of chess, not of the instance).
    knight_moves = [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)]

    model = cp.Model()

    # Each square is visited exactly once.
    model += cp.AllDifferent(x)

    # Encoding choice: a tour visiting every square once is a Hamiltonian path. A Circuit
    # constraint states that directly and propagates much better than comparing move numbers
    # of all neighbouring squares. Circuit needs a cycle, so a dummy node `cells` closes the
    # path: the dummy's successor is the first square, the last square's successor is the dummy.
    # nxt[c] = the square visited right after square c (c = i * n + j), or `cells` if c is last.
    nxt = cp.intvar(0, cells, shape=cells + 1, name="nxt")
    model += cp.Circuit(nxt)

    # From a square the knight can only go to a square a knight's move away (or end the tour).
    for i in range(n):
        for j in range(n):
            reachable = [(i + di) * n + (j + dj) for di, dj in knight_moves
                         if 0 <= i + di < n and 0 <= j + dj < n]
            model += cp.InDomain(nxt[i * n + j], reachable + [cells])

    # Link the successor structure to the move numbers: the square after c is visited one move
    # later, the first square is visited at move 0. `rank` is x flattened plus the dummy node.
    rank = cp.cpm_array(list(x.flatten()) + [cp.intvar(cells, cells, name="dummy_rank")])
    model += rank[nxt[cells]] == 0
    for c in range(cells):
        model += (nxt[c] != cells).implies(rank[nxt[c]] == rank[c] + 1)

    return model, {"x": x}
