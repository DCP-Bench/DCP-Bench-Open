# Giant cat army: build a list of 24 integers from 0 to 60, starting at 0 and ending at 14, where
# each step adds 5, adds 7 or takes the square root, the elements are distinct, and 2, 10 and 14
# appear in that order (other numbers may lie between them).
from pyscipopt import Model, quicksum

LENGTH = 24     # the list has 24 elements
MAX_VALUE = 60  # all elements are at most 60
TARGET = [2, 10, 14]  # the numbers that must appear, in this order
END = 14        # the list ends with 14
BIG_M = MAX_VALUE * MAX_VALUE  # bounds x[i] - x[i+1]**2 on the square-root step, since x[i+1]**2 <= 3600


def build(instance):
    m = Model()
    values = range(MAX_VALUE + 1)

    # x[i] is the i-th element of the list, an integer from 0 to 60
    x = [m.addVar(name=f"x_{i}", vtype="I", lb=0, ub=MAX_VALUE) for i in range(LENGTH)]

    # z[i, v] = 1 if the i-th element equals v: the one-hot encoding of x[i]
    z = {(i, v): m.addVar(name=f"z_{i}_{v}", vtype="B") for i in range(LENGTH) for v in values}
    for i in range(LENGTH):
        # each position holds exactly one value
        m.addCons(quicksum(z[i, v] for v in values) == 1)
        m.addCons(x[i] == quicksum(v * z[i, v] for v in values))

    # all elements are distinct: each value appears at most once in the list
    for v in values:
        m.addCons(quicksum(z[i, v] for i in range(LENGTH)) <= 1)

    # the list starts with 0
    m.addCons(x[0] == 0)

    # the list ends with 14
    m.addCons(x[LENGTH - 1] == END)

    # the numbers 2, 10 and 14 appear in that order: 2 appears once, 10 appears once and only after
    # the 2; 14 is the last element, so it comes after both
    m.addCons(quicksum(z[i, TARGET[0]] for i in range(LENGTH)) == 1)
    m.addCons(quicksum(z[i, TARGET[1]] for i in range(LENGTH)) == 1)
    for i in range(LENGTH):
        # a 10 at position i needs a 2 strictly before position i
        m.addCons(z[i, TARGET[1]] <= quicksum(z[j, TARGET[0]] for j in range(i)))

    # each step is one of three operations: add 5, add 7, or take the square root
    add5 = {i: m.addVar(name=f"add5_{i}", vtype="B") for i in range(LENGTH - 1)}
    add7 = {i: m.addVar(name=f"add7_{i}", vtype="B") for i in range(LENGTH - 1)}
    root = {i: m.addVar(name=f"sqrt_{i}", vtype="B") for i in range(LENGTH - 1)}
    for i in range(LENGTH - 1):
        m.addCons(add5[i] + add7[i] + root[i] == 1)

        # when the step adds 5, the next element is the current one plus 5 (two indicators give equality)
        m.addConsIndicator(x[i + 1] - x[i] >= 5, binvar=add5[i])
        m.addConsIndicator(x[i + 1] - x[i] <= 5, binvar=add5[i])

        # when the step adds 7, the next element is the current one plus 7
        m.addConsIndicator(x[i + 1] - x[i] >= 7, binvar=add7[i])
        m.addConsIndicator(x[i + 1] - x[i] <= 7, binvar=add7[i])

        # when the step takes the square root, the current element is the square of the next one;
        # the indicator form does not take nonlinear terms, so this is a big-M form
        m.addCons(x[i] - x[i + 1] * x[i + 1] <= BIG_M * (1 - root[i]))
        m.addCons(x[i + 1] * x[i + 1] - x[i] <= BIG_M * (1 - root[i]))

    outputs = {"x": x}
    return m, outputs
