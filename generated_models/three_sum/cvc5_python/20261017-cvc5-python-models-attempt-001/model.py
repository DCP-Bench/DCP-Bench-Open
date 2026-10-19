# Three sum: given a collection of integers, find a number of elements that
# sum to zero. The model reports, for each element, whether it is selected.
import cvc5.pythonic as cz


def build(instance):
    nums = instance["nums"]
    m = instance["m"]
    n = len(nums)

    sel = [cz.Bool(f"b{i}") for i in range(n)]

    # Find a number of elements that sum to zero: exactly m elements are selected.
    constraints = [
        cz.Sum([cz.If(sel[i], 1, 0) for i in range(n)]) == m,
    ]

    # Find a number of elements that sum to zero: the selected elements sum to zero.
    constraints.append(
        cz.Sum([cz.If(sel[i], int(nums[i]), 0) for i in range(n)]) == 0
    )

    return constraints, {"indices": sel}
