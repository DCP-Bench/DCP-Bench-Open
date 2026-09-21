# Eighteen holes of par 3, 4 or 5 adding up to a par-72 course.
# The course specification is the puzzle, so the instance carries no fields.
from dcp_sat import Sat


def build(instance):
    sat = Sat()
    holes = sat.ints(18, 3, 5)
    sat.sum_eq(holes, 72)
    return sat, {"holes": holes}
