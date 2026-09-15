from ortools.sat.python import cp_model


def build(instance):
    """People in a room: order the arrivals so the ratio of females to males
    never exceeds seven to three.

    The puzzle states its own thirteen people, so `instance` is unused.
    A 1 in the sequence is a female arrival and a 0 a male one.
    """
    del instance

    total_people = 13
    num_males = 4

    model = cp_model.CpModel()
    sequence = [model.new_bool_var(f"s{i}") for i in range(total_people)]

    model.add(sum(sequence) == total_people - num_males)
    for i in range(1, total_people):
        females = sum(sequence[:i])
        males = i - sum(sequence[:i])
        # Three females per seven males at most, cleared of the fraction.
        model.add(3 * females <= 7 * males)

    return model, {"sequence": sequence}
