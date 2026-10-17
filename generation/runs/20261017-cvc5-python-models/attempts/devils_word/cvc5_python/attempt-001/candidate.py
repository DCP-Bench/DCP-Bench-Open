# Devil's word: insert '+' or '-' operators before each integer of the array so that
# summing them up results in the total. The output is the array with the signs applied.
import cvc5.pythonic as cz


def build(instance):
    arr = instance["arr"]
    total = instance["total"]
    n = len(arr)

    result = [cz.Int(f"r{i}") for i in range(n)]

    # insert '+' or '-' operators before each integer in the array
    constraints = [cz.Or(r == a, r == -a) for r, a in zip(result, arr)]

    # summing them up will result in the total
    constraints.append(cz.Sum(result) == total)

    return constraints, {"result": result}
