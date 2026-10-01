# Quasigroup completion: complete a partially filled N-by-N table so that every row and
# every column contains each of 1..N exactly once (a Latin square).
import cpmpy as cp


def build(instance):
    N = instance["N"]            # order of the quasigroup
    start = instance["start"]    # start[i][j] is the given value, or 0 for an empty cell

    puzzle = cp.intvar(1, N, shape=(N, N), name="puzzle")

    model = cp.Model()

    # The cells that are already filled keep their given value.
    for i in range(N):
        for j in range(N):
            if start[i][j] != 0:
                model += puzzle[i, j] == start[i][j]

    # Each row contains every value exactly once.
    for i in range(N):
        model += cp.AllDifferent(puzzle[i, :])

    # Each column contains every value exactly once.
    for j in range(N):
        model += cp.AllDifferent(puzzle[:, j])

    return model, {"puzzle": puzzle}
