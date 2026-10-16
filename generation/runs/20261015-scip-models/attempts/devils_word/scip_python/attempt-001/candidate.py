# Devil's word: insert a '+' or '-' before each integer of arr so that the signed
# integers add up to total. The output lists the signed integers.
from pyscipopt import Model, quicksum


def build(instance):
    arr = instance["arr"]
    total = instance["total"]
    n = len(arr)

    m = Model()

    # plus[i] = 1 if the sign before the i-th integer is '+', 0 if it is '-'
    plus = [m.addVar(name=f"plus_{i}", vtype="B") for i in range(n)]
    # signed[i] = the i-th integer with its sign applied
    signed = [
        m.addVar(name=f"signed_{i}", vtype="I", lb=-abs(arr[i]), ub=abs(arr[i]))
        for i in range(n)
    ]

    # each integer is kept or negated according to its sign
    for i in range(n):
        m.addCons(signed[i] == arr[i] * (2 * plus[i] - 1))

    # the signed integers must sum to the total
    m.addCons(quicksum(signed) == total)

    return m, {"result": signed}
