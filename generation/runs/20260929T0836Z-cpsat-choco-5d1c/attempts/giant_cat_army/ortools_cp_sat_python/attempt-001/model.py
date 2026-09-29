# Giant cat army riddle: start from [0] and extend the list by adding 5, adding
# 7 or taking a square root, so that all numbers are different integers of at
# most 60, the list contains 2, then 10, then 14 (in that order), and it ends
# with 14 after exactly 24 numbers.
from ortools.sat.python import cp_model

# The riddle fixes these numbers, so they are mirrored here.
MAX_VALUE = 60  # largest number allowed in the list
LENGTH = 24  # number of entries in the list
GOAL = 14  # the last entry


def build(instance):
    model = cp_model.CpModel()

    # x[i] = the i-th number of the list
    x = [model.new_int_var(0, MAX_VALUE, f"x_{i}") for i in range(LENGTH)]

    # all numbers are different
    model.add_all_different(x)

    # the list starts with 0 and ends with 14
    model.add(x[0] == 0)
    model.add(x[LENGTH - 1] == GOAL)

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
    moves = sorted(moves)
    for i in range(LENGTH - 1):
        model.add_allowed_assignments([x[i], x[i + 1]], moves)

    # the list contains 2 and later 10 (and, as it ends with it, 14 after both)
    index_of_2 = model.new_int_var(1, LENGTH - 1, "index_of_2")
    index_of_10 = model.new_int_var(1, LENGTH - 1, "index_of_10")
    model.add_element(index_of_2, x, 2)
    model.add_element(index_of_10, x, 10)
    model.add(index_of_2 < index_of_10)

    return model, {"x": x}
