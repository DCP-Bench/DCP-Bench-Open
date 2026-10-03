# Four numbers: given up to four distinct integers between 1 and 10, find three integers
# between 1 and 10 such that each given number is the sum of some subset of the three.
from pychoco.model import Model

N_SUMMANDS = 3  # the problem asks for exactly three integers


def build(instance):
    numbers = instance["numbers"]  # the numbers that must be generated
    m = len(numbers)

    model = Model()

    # x[j] = the j-th of the three integers, each between 1 and 10
    x = [model.intvar(1, 10, name=f"x_{j}") for j in range(N_SUMMANDS)]
    # chosen[i][j] = 1 if x[j] is part of the subset that sums to numbers[i]
    chosen = [[model.boolvar(name=f"chosen_{i}_{j}") for j in range(N_SUMMANDS)] for i in range(m)]

    # each given number is the sum of the chosen subset of x
    for i in range(m):
        # contribution[j] = x[j] if it is chosen for numbers[i], else 0
        contribution = [model.intvar(0, 10, name=f"contribution_{i}_{j}") for j in range(N_SUMMANDS)]
        for j in range(N_SUMMANDS):
            model.times(x[j], chosen[i][j], contribution[j]).post()
        model.sum(contribution, "=", numbers[i]).post()

    return model, {"x": x}
