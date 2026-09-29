# Devil's word: put a plus or minus sign in front of every number of a list so
# that the signed numbers add up to the given total.
from exact import Exact


def build(instance):
    arr = instance["arr"]  # the numbers, in order
    total = instance["total"]  # the sum the signed numbers must reach
    n = len(arr)

    solver = Exact()
    # plus[i] is 1 when arr[i] is added and 0 when it is subtracted
    plus = [f"plus_{i}" for i in range(n)]
    # result[i] = arr[i] with its chosen sign, that is 2 * arr[i] * plus[i] - arr[i]
    result = [f"result_{i}" for i in range(n)]
    for i in range(n):
        solver.addVariable(plus[i], 0, 1)
        solver.addVariable(result[i], -abs(arr[i]), abs(arr[i]))
        solver.addConstraint([(1, result[i]), (-2 * arr[i], plus[i])], True, -arr[i], True, -arr[i])

    # the signed numbers add up to the total
    solver.addConstraint([(1, name) for name in result], True, total, True, total)

    return solver, {"result": result}
