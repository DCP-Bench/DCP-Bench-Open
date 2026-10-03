"""Devil's word: put a + or - sign before each number of the array so that the signed numbers sum to the given total."""
import gurobipy as gp
from gurobipy import GRB


def build(instance):
    arr = instance["arr"]
    total = instance["total"]
    n = len(arr)

    model = gp.Model("devils_word")

    # plus[i] is 1 when arr[i] is added and 0 when it is subtracted, so each
    # number gets exactly one of the two signs.
    plus = [model.addVar(vtype=GRB.BINARY, name=f"plus[{i}]") for i in range(n)]

    # The number with its sign: arr[i] when added, -arr[i] when subtracted.
    result = [arr[i] * (2 * plus[i] - 1) for i in range(n)]

    # The signed numbers sum to the total.
    model.addConstr(gp.quicksum(result) == total, name="total")

    return model, {"result": result}
