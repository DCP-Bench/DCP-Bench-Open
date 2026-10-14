# People in a room: 13 people, 4 of them male, enter a room one at a time. Find an order of
# males and females so that the ratio of females to males in the room never exceeds 7/3.
from hermax.model import Model


def build(instance):
    # The numbers are fixed by the problem; the instance carries no data.
    total_people = 13
    num_males = 4

    m = Model()
    # sequence[i] = the i-th person to enter is female (false: male)
    sequence = m.bool_vector("sequence", total_people)

    # exactly 13 - 4 = 9 females enter
    m &= (sum(sequence[i] for i in range(total_people)) == total_people - num_males)

    # After the first i people have entered, females : males <= 7 : 3, that is
    # 3 * females <= 7 * (i - females), or females <= 7 * i / 10 (rounded down).
    for i in range(1, total_people):
        m &= (sum(sequence[k] for k in range(i)) <= 7 * i // 10)

    return m, {"sequence": sequence}
