# Eighteen-hole golf: choose the length of each of 18 holes, every hole being 3, 4 or 5 long, so
# that the whole course is 72 long.
from exact import Exact


def build(instance):
    # This problem has no instance data. The number of holes, the allowed lengths and the course
    # length belong to the problem statement.
    num_holes = 18
    total_length = 72
    shortest, longest = 3, 5  # the allowed hole lengths are 3, 4 and 5

    solver = Exact()
    # holes[i] is the length of hole i
    holes = [f"holes_{i}" for i in range(num_holes)]
    for name in holes:
        solver.addVariable(name, shortest, longest)

    # The total length of the course is 72.
    solver.addConstraint([(1, name) for name in holes], True, total_length, True, total_length)

    return solver, {"holes": holes}
