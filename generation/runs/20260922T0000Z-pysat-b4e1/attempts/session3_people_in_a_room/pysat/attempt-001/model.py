# Order thirteen arrivals so the room is never more than 7 women to 3 men.
# The head counts are the puzzle, so the instance carries no fields.
from dcp_sat import Sat


def build(instance):
    total_people = 13
    num_males = 4

    sat = Sat()
    # true is a woman, false a man
    sequence = sat.bools(total_people)
    sat.exactly(sequence, total_people - num_males)

    # After i arrivals: 3 * women <= 7 * men, with men = i - women, so
    # 10 * women <= 7 * i.
    for i in range(1, total_people):
        sat.bool_sum_le([10] * i, sequence[:i], 7 * i)
    return sat, {"sequence": sequence}
