# Giant cat army riddle: start from [0] and extend the list by adding 5, adding
# 7 or taking a square root, so that all numbers are different integers of at
# most 60, the list contains 2, then 10, then 14 (in that order), and it ends
# with 14 after exactly 24 numbers.
from hermax.model import Model

# The riddle fixes these numbers, so they are mirrored here.
MAX_VALUE = 60  # largest number allowed in the list
LENGTH = 24  # number of entries in the list
GOAL = 14  # the last entry


def build(instance):
    m = Model()
    # x[i] = the i-th number of the list, all different
    x = m.int_vector("x", LENGTH, 0, MAX_VALUE)
    m &= x.all_different()

    # the list starts with 0 and ends with 14
    m &= (x[0] == 0)
    m &= (x[LENGTH - 1] == GOAL)

    # each number follows the previous one by adding 5, adding 7, or taking the
    # square root (the previous number is the square of the next one), so every
    # pair (x[i], x[i+1]) is one of these moves
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
        m &= m.vector([x[i], x[i + 1]]).is_in(moves)

    # the list contains 2 and later 10: 10 appears, and wherever it does, 2 comes earlier
    appears = x[0] == 10
    for j in range(1, LENGTH):
        appears = appears | (x[j] == 10)
    m &= appears
    for j in range(1, LENGTH):
        clause = ~(x[j] == 10)
        for i in range(1, j):
            clause = clause | (x[i] == 2)
        m &= clause

    return m, {"x": x}
