# Langford's problem: arrange two copies of each of the numbers 1..k in a sequence
# of length 2k so that the two copies of the number i have exactly i numbers
# between them (they are i + 1 positions apart).
from pychoco.model import Model


def build(instance):
    k = instance["k"]

    model = Model()

    # position[i - 1] = where the first copy of number i is placed,
    # position[k + i - 1] = where its second copy is placed (positions 0..2k-1)
    position = [model.intvar(0, 2 * k - 1, name=f"position_{j}") for j in range(2 * k)]
    # sol[p] = the number placed at position p
    sol = [model.intvar(1, k, name=f"sol_{p}") for p in range(2 * k)]

    # every one of the 2k copies sits at its own position
    model.all_different(position).post()

    for i in range(1, k + 1):
        # the two copies of i are i + 1 positions apart
        model.arithm(position[i - 1], "+", i + 1, "=", position[i + k - 1]).post()
        # the number at the position of each copy of i is i
        model.element(model.intvar(i, i), sol, position[i - 1]).post()
        model.element(model.intvar(i, i), sol, position[k + i - 1]).post()

    return model, {"sol": sol}
