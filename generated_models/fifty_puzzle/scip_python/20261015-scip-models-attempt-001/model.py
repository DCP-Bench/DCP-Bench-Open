# Problem: choose which dummies to knock over so that the numbers on them add up to exactly the target sum.
from pyscipopt import Model, quicksum


def build(instance):
    values = instance["values"]
    target = instance["target_sum"]
    n = len(values)

    m = Model()
    # knocked[i] = 1 if dummy i is knocked over
    knocked = [m.addVar(name=f"knocked_{i}", vtype="B") for i in range(n)]

    # the numbers on the dummies knocked over add up to exactly the target sum, neither more nor less
    m.addCons(quicksum(values[i] * knocked[i] for i in range(n)) == target)

    return m, {"dummies": knocked}
