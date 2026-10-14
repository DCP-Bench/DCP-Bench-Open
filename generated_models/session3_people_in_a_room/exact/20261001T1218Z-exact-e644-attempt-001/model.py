# People in a room: 13 people, 4 of them male, enter a room one at a time. Order them so that at
# every moment the ratio of females to males in the room is at most 7/3.
from exact import Exact


def build(instance):
    # This problem has no instance data. The head-counts and the ratio belong to the problem statement.
    total_people = 13
    num_males = 4
    ratio_females, ratio_males = 7, 3  # females : males <= 7 : 3

    solver = Exact()
    # sequence[i] = 1 when the i-th person to enter is female, 0 when male
    sequence = [f"sequence_{i}" for i in range(total_people)]
    for name in sequence:
        solver.addVariable(name, 0, 1)

    # Exactly total_people - num_males of the people are female.
    females = total_people - num_males
    solver.addConstraint([(1, name) for name in sequence], True, females, True, females)

    # After each of the first i people (i = 1 .. total - 1) have entered, the number of females is
    # at most 7/3 of the number of males. With F females among i people there are i - F males, and
    # F / (i - F) <= 7/3 is  3 F <= 7 (i - F), i.e.  (3 + 7) F <= 7 i.
    for i in range(1, total_people):
        solver.addConstraint([(ratio_males + ratio_females, name) for name in sequence[:i]],
                             False, 0, True, ratio_females * i)

    return solver, {"sequence": sequence}
