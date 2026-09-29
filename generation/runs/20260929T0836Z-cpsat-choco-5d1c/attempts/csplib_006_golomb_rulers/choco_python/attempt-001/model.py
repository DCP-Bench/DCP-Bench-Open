# Golomb ruler: place `size` marks at integer positions 0 = a_1 < a_2 < ... so
# that all the differences between two marks are distinct, with the ruler as
# short as possible (the last mark is as small as possible).
from pychoco.model import Model


def build(instance):
    size = instance["size"]  # number of marks

    model = Model()

    # marks[i] = position of mark i; a mark never needs to lie beyond size * size
    marks = [model.intvar(0, size * size, name=f"marks_{i}") for i in range(size)]

    # the first mark is at 0
    model.arithm(marks[0], "=", 0).post()
    # the marks are in increasing order
    for i in range(size - 1):
        model.arithm(marks[i], "<", marks[i + 1]).post()

    # all differences between pairs of marks are different
    differences = []
    for i in range(size - 1):
        for j in range(i + 1, size):
            difference = model.intvar(1, size * size, name=f"difference_{i}_{j}")
            model.arithm(marks[j], "-", marks[i], "=", difference).post()
            differences.append(difference)
    model.all_different(differences).post()

    # the length of the ruler is the position of the last mark, to be minimised
    length = marks[size - 1]

    return model, {"marks": marks, "length": length}, ("minimize", length)
