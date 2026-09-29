# Guards and apples: a boy passes several gates. At each gate he gives the guard
# half of his apples plus one, and after the last gate one apple is left for the girl.
from hermax.model import Model


def build(instance):
    num_gates = instance["num_gates"]

    m = Model()
    # apples[i] = the apples the boy has before gate i; the last entry is what he has
    # after the last gate. The apples are between 0 and 100.
    apples = m.int_vector("apples", num_gates + 1, 0, 100)

    # after the last gate the boy keeps the one apple he gives to the girl
    m &= (apples[num_gates] == 1)

    # at each gate the guard gets half of the apples plus one, so the boy is left
    # with half of them minus one: before = 2 * (after + 1)
    for i in range(1, num_gates + 1):
        m &= (apples[i - 1] == 2 * apples[i] + 2)

    return m, {"apples": apples}
