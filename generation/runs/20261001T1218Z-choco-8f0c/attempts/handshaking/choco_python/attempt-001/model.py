# Handshaking (Halmos): Hilary and Jocelyn are married and invite some couples. Everybody
# shakes hands with some of the others, never with themselves or their spouse. Everybody
# except Hilary gives a different number of handshakes. How many hands did Hilary shake?
from pychoco.model import Model


def build(instance):
    num_couples = instance["num_couples"]  # couples invited, excluding Hilary and Jocelyn
    n = 2 + num_couples * 2  # number of people

    model = Model()

    # People are numbered in couples: 0 and 1 are Hilary and Jocelyn, 2 and 3 are the first
    # invited couple, and so on, so the spouse of person i is i ^ 1.
    # shakes[i][j] (i < j) = 1 if persons i and j shake hands. Nobody shakes hands with
    # themselves or their spouse, so those pairs get no variable. Handshaking is symmetric,
    # hence one variable stands for both directions.
    shakes = {}
    for i in range(n):
        for j in range(i + 1, n):
            if j != (i ^ 1):
                shakes[(i, j)] = model.boolvar(name=f"shakes_{i}_{j}")

    # x[i] = number of hands person i has shaken; nobody can shake more than n - 2 hands
    x = [model.intvar(0, n - 2, name=f"x_{i}") for i in range(n)]
    for i in range(n):
        hands = [shakes[(min(i, j), max(i, j))] for j in range(n) if j != i and j != (i ^ 1)]
        model.sum(hands, "=", x[i]).post()

    # everybody except Hilary (person 0) gave a different number of handshakes
    model.all_different(x[1:]).post()

    hil = x[0]  # Hilary's handshakes
    return model, {"hil": hil}
