# Devil's word: put a plus or minus sign in front of every number of a list so
# that the signed numbers add up to the given total.
import z3


def build(instance):
    arr = instance["arr"]  # the numbers, in order
    total = instance["total"]  # the sum the signed numbers must reach

    solver = z3.Solver()

    # result[i] = arr[i] with its chosen sign: either +arr[i] or -arr[i]
    result = [z3.Int(f"result_{i}") for i in range(len(arr))]
    for i, value in enumerate(arr):
        solver.add(z3.Or(result[i] == value, result[i] == -value))

    # the signed numbers add up to the total
    solver.add(z3.Sum(result) == total)

    return solver, {"result": result}
