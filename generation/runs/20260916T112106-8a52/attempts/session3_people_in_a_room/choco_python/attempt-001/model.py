from pychoco.model import Model


def build(instance):
    """People in a room: order the arrivals so the ratio of females to males
    never exceeds seven to three.  A 1 is a female arrival.
    """
    del instance

    total_people = 13
    num_males = 4

    model = Model()
    sequence = [model.boolvar(name=f"s{i}") for i in range(total_people)]

    model.sum(sequence, "=", total_people - num_males).post()

    for i in range(1, total_people):
        # Three females per seven males at most, cleared of the fraction:
        # 3F <= 7(i - F) is 10F <= 7i over the first i arrivals.
        model.scalar(sequence[:i], [10] * i, "<=", 7 * i).post()

    return model, {"sequence": sequence}
