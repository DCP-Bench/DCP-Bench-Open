# Guards and apples: a boy passes several gates. At each gate he gives the guard
# half of his apples plus one, and after the last gate one apple is left for the girl.
from exact import Exact


def build(instance):
    num_gates = instance["num_gates"]

    solver = Exact()
    # apples[i] = the apples the boy has before gate i; the last entry is what he has
    # after the last gate. The apples are between 0 and 100.
    apples = [f"apples_{i}" for i in range(num_gates + 1)]
    for name in apples:
        solver.addVariable(name, 0, 100)

    # after the last gate the boy keeps the one apple he gives to the girl
    solver.addConstraint([(1, apples[num_gates])], True, 1, True, 1)

    # at each gate the guard gets half of the apples plus one, so the boy is left
    # with half of them minus one: before = 2 * (after + 1)
    for i in range(1, num_gates + 1):
        solver.addConstraint([(1, apples[i - 1]), (-2, apples[i])], True, 2, True, 2)

    return solver, {"apples": apples}
