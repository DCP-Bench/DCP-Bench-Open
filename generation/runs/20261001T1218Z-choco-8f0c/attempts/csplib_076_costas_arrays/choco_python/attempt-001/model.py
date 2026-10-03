# Costas array: a permutation of 1..n (one mark per row and column of an n x n grid)
# such that the vectors between all pairs of marks are different, i.e. in the
# difference triangle no row contains a value twice.
from pychoco.model import Model


def build(instance):
    n = instance["n"]  # size of the array

    model = Model()

    # costas[j] = the row (1..n) of the mark in column j
    costas = [model.intvar(1, n, name=f"costas_{j}") for j in range(n)]

    # one mark per row: the values of costas form a permutation
    model.all_different(costas).post()

    # difference triangle: for every distance lag between two columns, the
    # differences costas[j] - costas[j - lag] must all be different. The lag n - 1
    # has a single difference, so there is nothing to compare for it.
    for lag in range(1, n - 1):
        row = []
        for j in range(lag, n):
            difference = model.intvar(-(n - 1), n - 1, name=f"difference_{lag}_{j}")
            model.arithm(costas[j], "-", costas[j - lag], "=", difference).post()
            row.append(difference)
        model.all_different(row).post()

    return model, {"costas": costas}
