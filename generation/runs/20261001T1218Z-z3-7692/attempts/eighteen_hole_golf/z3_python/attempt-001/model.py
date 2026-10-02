# Eighteen-hole golf: lay out a course of 18 holes, each of length 3, 4 or 5,
# so that the whole course has length 72.
import z3


def build(instance):
    del instance  # the puzzle states its own course size

    num_holes = 18
    total_length = 72
    shortest, longest = 3, 5  # each hole has length 3, 4 or 5

    # holes[i] = length of hole i.
    holes = z3.IntVector("holes", num_holes)

    solver = z3.Solver()
    for h in holes:
        solver.add(h >= shortest, h <= longest)

    # The total length of the course is 72.
    solver.add(z3.Sum(holes) == total_length)

    return solver, {"holes": list(holes)}
