# Golomb ruler: place `size` marks at integer positions 0 = a_1 < a_2 < ... so
# that all the differences between two marks are distinct, with the ruler as
# short as possible (the last mark is as small as possible).
from ortools.sat.python import cp_model


def build(instance):
    size = instance["size"]  # number of marks

    model = cp_model.CpModel()

    # marks[i] = position of mark i; a mark never needs to lie beyond size * size
    marks = [model.new_int_var(0, size * size, f"marks_{i}") for i in range(size)]

    # the first mark is at 0
    model.add(marks[0] == 0)
    # the marks are in increasing order
    for i in range(size - 1):
        model.add(marks[i] < marks[i + 1])

    # all differences between pairs of marks are different
    differences = [marks[j] - marks[i] for i in range(size - 1) for j in range(i + 1, size)]
    model.add_all_different(differences)

    # the length of the ruler is the position of the last mark, to be minimised
    length = marks[size - 1]
    model.minimize(length)

    return model, {"marks": marks, "length": length}
