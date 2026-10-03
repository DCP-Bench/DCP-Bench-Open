"""People in a room: 13 people, 4 of them male, enter a room one at a time; order them so
that the ratio of females to males in the room is never above 7/3.
"""
from docplex.mp.model import Model


def build(instance):
    # The problem has no instance data; the counts and the ratio are from the statement.
    total_people = 13
    num_males = 4

    model = Model("people_in_a_room")

    # sequence[i] is 1 when the i-th person to enter is female, 0 when male.
    sequence = [model.binary_var(name=f"female_{i}") for i in range(total_people)]

    # Exactly 13 - 4 = 9 of them are female.
    model.add_constraint(model.sum(sequence) == total_people - num_males)

    # After each of the first i entries (i = 1..12, as in the reference), females to males
    # is at most 7/3: 3 * females <= 7 * males, with males = i - females.
    for i in range(1, total_people):
        model.add_constraint(3 * model.sum(sequence[:i]) <= 7 * (i - model.sum(sequence[:i])))

    return model, {"sequence": sequence}
