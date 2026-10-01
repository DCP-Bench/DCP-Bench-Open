# Golomb rulers: place `size` marks on a ruler, first mark at 0, so that all pairwise
# differences between marks are distinct, and make the ruler as short as possible.
import cpmpy as cp


def build(instance):
    size = instance["size"]  # number of marks on the ruler

    # Position of each mark. The upper bound size * size is the one the problem's
    # reference uses; a ruler with `size` marks needs far less than that.
    marks = cp.intvar(0, size * size, shape=size, name="marks")
    # The length of the ruler is the position of the last mark.
    length = marks[size - 1]

    model = cp.Model()

    # The first mark is at position 0.
    model += marks[0] == 0

    # Marks are placed in strictly increasing order of position.
    for i in range(size - 1):
        model += marks[i] < marks[i + 1]

    # Golomb condition: the differences between every pair of marks are all distinct.
    diffs = [marks[j] - marks[i] for i in range(size - 1) for j in range(i + 1, size)]
    model += cp.AllDifferent(diffs)

    # Find the shortest ruler.
    model.minimize(length)

    return model, {"marks": marks, "length": length}
