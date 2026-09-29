# Giant cat army riddle: start from [0] and extend the list by adding 5, adding
# 7 or taking a square root, so that all numbers are different integers of at
# most 60, the list contains 2, then 10, then 14 (in that order), and it ends
# with 14 after exactly 24 numbers.
from pychoco.model import Model

# The riddle fixes these numbers, so they are mirrored here.
MAX_VALUE = 60  # largest number allowed in the list
LENGTH = 24  # number of entries in the list
GOAL = 14  # the last entry


def build(instance):
    model = Model()

    # x[i] = the i-th number of the list
    x = [model.intvar(0, MAX_VALUE, name=f"x_{i}") for i in range(LENGTH)]

    # all numbers are different
    model.all_different(x).post()

    # the list starts with 0 and ends with 14
    model.arithm(x[0], "=", 0).post()
    model.arithm(x[LENGTH - 1], "=", GOAL).post()

    # each number follows the previous one by adding 5, adding 7, or taking the
    # square root (the previous number x[i] is the square of the next x[i+1]).
    # All three moves are listed as allowed pairs (x[i], x[i+1]).
    moves = set()
    for v in range(MAX_VALUE + 1):
        if v + 5 <= MAX_VALUE:
            moves.add((v, v + 5))
        if v + 7 <= MAX_VALUE:
            moves.add((v, v + 7))
        if v * v <= MAX_VALUE:
            moves.add((v * v, v))
    moves = [list(pair) for pair in sorted(moves)]
    for i in range(LENGTH - 1):
        model.table([x[i], x[i + 1]], moves).post()

    # the list contains 2 and later 10 (and, as it ends with it, 14 after both).
    # Choco's element constraint takes the sought value as a variable, so 2 and
    # 10 are given as constant variables.
    two = model.intvar(2, 2, name="two")
    ten = model.intvar(10, 10, name="ten")
    index_of_2 = model.intvar(1, LENGTH - 1, name="index_of_2")
    index_of_10 = model.intvar(1, LENGTH - 1, name="index_of_10")
    model.element(two, x, index_of_2).post()
    model.element(ten, x, index_of_10).post()
    model.arithm(index_of_2, "<", index_of_10).post()

    return model, {"x": x}
