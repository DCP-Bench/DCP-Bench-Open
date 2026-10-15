"""Giant cat army (list-building game).

Start from [0] and build a list of 24 integers, ending with 14. Each step adds 5, adds 7,
or takes the square root (an integer result only). The elements are distinct and at most 60.
The numbers 2, 10 and 14 appear in that order; other numbers may lie between them.
The problem has no instance data: the start, end, length and bounds come from the statement.
"""

from math import isqrt

from paramita.modelling import Bool, If

LENGTH = 24  # the list has 24 elements, x[0] = 0, x[23] = 14
MAX_VALUE = 60  # all elements are at most 60
START, END = 0, 14
TARGETS_IN_ORDER = (2, 10, 14)
OPERATIONS = ("add5", "add7", "sqrt")


def successor(v, op):
    """The element that operation op gives from v, or None when it is not allowed."""
    if op == "add5":
        w = v + 5
    elif op == "add7":
        w = v + 7
    else:
        w = isqrt(v)
        if w * w != v:  # only integer square roots
            return None
    return w if w <= MAX_VALUE else None


def build(instance):
    values = range(MAX_VALUE + 1)

    # p[i][v] = 1 if element i of the list is v (one-hot)
    p = [{v: Bool(f"p_{i}_{v}") for v in values} for i in range(LENGTH)]
    # op[i][k] = 1 if step i (from element i to element i+1) uses operation k
    op = [{k: Bool(f"op_{i}_{k}") for k in OPERATIONS} for i in range(LENGTH - 1)]

    cons = []

    # every position of the list holds exactly one number
    cons += [sum(p[i].values()) == 1 for i in range(LENGTH)]

    # the list starts with 0 (x[0]) and ends with 14 (x[23])
    cons.append(p[0][START])
    cons.append(p[LENGTH - 1][END])

    # each step uses exactly one of the three operations
    cons += [sum(op[i].values()) == 1 for i in range(LENGTH - 1)]

    # all the elements are distinct
    cons += [sum(p[i][v] for i in range(LENGTH)) <= 1 for v in values]

    # each step: adding 5, adding 7, or taking the square root gives the next element
    for i in range(LENGTH - 1):
        for v in values:
            for k in OPERATIONS:
                w = successor(v, k)
                if w is None:
                    cons.append(~(p[i][v] & op[i][k]))
                else:
                    cons.append(If(p[i][v] & op[i][k], p[i + 1][w]))

    # 2, 10 and 14 appear on the list, in that order (14 is the last element)
    two, ten, _ = TARGETS_IN_ORDER
    cons.append(sum(p[i][two] for i in range(LENGTH)) == 1)
    cons.append(sum(p[i][ten] for i in range(LENGTH)) == 1)
    # 10 comes after 2
    for j in range(1, LENGTH):
        cons.append(If(p[j][ten], sum(p[i][two] for i in range(j)) >= 1))

    outputs = {"x": [sum(v * p[i][v] for v in values) for i in range(LENGTH)]}
    return cons, outputs
