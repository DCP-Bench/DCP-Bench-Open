"""Devil's word: put a '+' or a '-' before each integer of a list so that the signed numbers
add up to a given total.

The model reports the list with its signs applied.
"""
import pulp


def build(instance):
    arr = instance["arr"]  # the integers
    total = instance["total"]  # the sum to reach
    n = len(arr)

    problem = pulp.LpProblem("devils_word", pulp.LpMinimize)  # satisfaction: no objective

    # plus[i] = 1 if arr[i] gets a '+', 0 if it gets a '-'. A zero has the same value with
    # either sign, so it is kept '+' to avoid duplicate solutions with the same output.
    plus = [pulp.LpVariable(f"plus_{i}", cat="Binary") for i in range(n)]
    for i in range(n):
        if arr[i] == 0:
            problem += plus[i] == 1

    # result[i] = arr[i] with its sign: +arr[i] if plus[i], -arr[i] otherwise
    result = [arr[i] * (2 * plus[i] - 1) for i in range(n)]

    # the signed numbers add up to the total
    problem += pulp.lpSum(result) == total

    return problem, {"result": result}
