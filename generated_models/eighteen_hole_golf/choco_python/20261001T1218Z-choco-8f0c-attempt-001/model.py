# Eighteen-hole golf: lay out 18 holes, each of length 3, 4 or 5, totalling 72.
from pychoco.model import Model

# The puzzle has no instance data; the hole count, lengths and total are its statement.
NUM_HOLES = 18
TOTAL_LENGTH = 72


def build(instance):
    del instance  # the puzzle carries no instance data

    model = Model()

    # holes[i] = the length of hole i, one of 3, 4 or 5
    holes = [model.intvar(3, 5, name=f"holes_{i}") for i in range(NUM_HOLES)]

    # The course is 72 long.
    model.sum(holes, "=", TOTAL_LENGTH).post()

    return model, {"holes": holes}
