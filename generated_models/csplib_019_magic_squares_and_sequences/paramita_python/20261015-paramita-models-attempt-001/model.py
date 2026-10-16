# Magic sequence: a sequence x_0..x_{n-1} with values between 0 and n-1 such that
# the number i occurs exactly x_i times in the sequence, for every i.
# Each x_i is a one-hot choice over the values 0..n-1.
from paramita.modelling import Bool


def build(instance):
    n = instance["n"]

    # x[i][w] = 1 if x_i takes the value w
    x = [{w: Bool(f"x_{i}_{w}") for w in range(n)} for i in range(n)]

    cons = []
    # every x_i takes exactly one value between 0 and n-1
    for i in range(n):
        cons.append(sum(x[i].values()) == 1)

    # the number i occurs exactly x_i times: the count of positions j with x_j = i
    # equals the value of x_i
    for i in range(n):
        occurrences = sum(x[j][i] for j in range(n))
        value = sum(w * x[i][w] for w in range(n))
        cons.append(occurrences == value)

    # the sequence values are the linear integer expressions over the one-hot Bools
    seq = [sum(w * x[i][w] for w in range(n)) for i in range(n)]

    return cons, {"x": seq}
