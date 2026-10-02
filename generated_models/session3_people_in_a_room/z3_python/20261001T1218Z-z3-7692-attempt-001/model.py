# People in a room: 13 people, 4 of them male, enter a room one at a time. Order
# them so that, at every moment, the ratio of females to males in the room is
# no greater than 7/3.
import z3


def build(instance):
    del instance  # the puzzle states its own people and ratio

    total_people = 13
    num_males = 4

    # sequence[i] is True when the ith person to enter is female, False when male.
    sequence = z3.BoolVector("sequence", total_people)

    solver = z3.Solver()

    # Exactly 4 of the 13 are male, so 9 are female.
    solver.add(z3.PbEq([(s, 1) for s in sequence], total_people - num_males))

    # After each of the first 12 entries, females : males <= 7 : 3, i.e.
    # 3 * females <= 7 * males (cross-multiplied to stay in integers).
    for i in range(1, total_people):
        females_so_far = z3.Sum([z3.If(s, 1, 0) for s in sequence[:i]])
        males_so_far = i - females_so_far
        solver.add(3 * females_so_far <= 7 * males_so_far)

    return solver, {"sequence": list(sequence)}
