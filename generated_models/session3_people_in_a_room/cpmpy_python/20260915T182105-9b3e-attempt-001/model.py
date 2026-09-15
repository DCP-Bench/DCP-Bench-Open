import cpmpy as cp


def build(instance):
    """People in a room: order the arrivals so the ratio of females to males
    never exceeds seven to three.

    The puzzle states its own thirteen people, so `instance` is unused.
    A 1 in the sequence is a female arrival and a 0 a male one.
    """
    del instance

    total_people = 13
    num_males = 4

    sequence = cp.boolvar(shape=total_people, name="sequence")

    model = cp.Model(cp.sum(sequence) == total_people - num_males)
    for i in range(1, total_people):
        females = cp.sum(sequence[:i])
        males = i - cp.sum(sequence[:i])
        # Three females per seven males at most, cleared of the fraction.
        model += 3 * females <= 7 * males

    return model, {"sequence": sequence}
