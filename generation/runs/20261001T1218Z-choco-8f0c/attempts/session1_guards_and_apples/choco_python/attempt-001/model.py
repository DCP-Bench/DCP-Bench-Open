# Guards and apples: a boy passes a number of gates to give an apple to a girl. At each
# gate he gives the guard half of his apples plus one, never cutting an apple, and after
# giving his last apple to the girl he has none left. How many apples does he have
# before each gate and after the last one?
from pychoco.model import Model

# Upper bound the reference declares on the number of apples at any point
# (it belongs to the problem, not the instance).
MAX_APPLES = 100


def build(instance):
    num_gates = instance["num_gates"]

    model = Model()

    # apples[i] = apples the boy has before gate i; apples[num_gates] = apples after the last gate
    apples = [model.intvar(0, MAX_APPLES, name=f"apples_{i}") for i in range(num_gates + 1)]

    # after the last gate he is left with 1 apple, which he gives to the girl
    model.arithm(apples[num_gates], "=", 1).post()

    # at each gate he gives the guard half of his apples plus one, i.e. what he has before
    # the gate is twice what he has after it plus one: before = 2 * (after + 1)
    for i in range(1, num_gates + 1):
        model.scalar([apples[i - 1], apples[i]], [1, -2], "=", 2).post()

    return model, {"apples": apples}
