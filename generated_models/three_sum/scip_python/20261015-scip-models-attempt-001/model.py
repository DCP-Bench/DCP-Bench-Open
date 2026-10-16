# Three-sum: select m of the given integers so that the selected numbers sum to zero.
from pyscipopt import Model, quicksum


def build(instance):
    nums = instance["nums"]
    m_count = instance["m"]
    n = len(nums)

    model = Model()

    # x[i] = 1 if the element nums[i] is selected
    x = [model.addVar(name=f"x_{i}", vtype="B") for i in range(n)]

    # select a number of elements, namely m of them
    model.addCons(quicksum(x) == m_count)

    # the selected elements sum to zero
    model.addCons(quicksum(nums[i] * x[i] for i in range(n)) == 0)

    # the output gives, for each element, whether it is selected
    return model, {"indices": x}
