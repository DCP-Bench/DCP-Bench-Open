# Kidney exchange: people on a waiting list can donate a kidney to some other people.
# Choose transplants so that as many people as possible receive a kidney, where anyone
# who gives a kidney must receive one, and nobody gives or receives more than one.
from pychoco.model import Model


def build(instance):
    num_people = instance["num_people"]
    compatible = instance["compatible"]  # compatible[i] = people (1-based) that person i can donate to
    n = num_people

    model = Model()

    # transplants[i][j] is true when person i donates to person j. A donation that is
    # not compatible can never happen, so that cell is the constant False instead of a variable.
    transplants = [[model.boolvar(name=f"transplants_{i}_{j}") if j + 1 in compatible[i] else False
                    for j in range(n)] for i in range(n)]

    for i in range(n):
        gives = [transplants[i][j] for j in range(n) if transplants[i][j] is not False]
        receives = [transplants[j][i] for j in range(n) if transplants[j][i] is not False]

        # each person donates to at most one person and receives from at most one person
        if gives:
            model.sum(gives, "<=", 1).post()
        if receives:
            model.sum(receives, "<=", 1).post()

        # anyone who gives a kidney must receive one. As both counts are at most 1,
        # "if gives >= 1 then receives >= 1" is the same as gives <= receives.
        if gives:
            model.scalar(gives + receives, [1] * len(gives) + [-1] * len(receives), "<=", 0).post()

    # number of transplants (Choco maximises one variable, so it gets its own)
    all_transplants = [t for row in transplants for t in row if t is not False]
    num_transplants = model.intvar(0, n, name="num_transplants")
    model.sum(all_transplants, "=", num_transplants).post()

    return model, {"transplants": transplants}, ("maximize", num_transplants)
