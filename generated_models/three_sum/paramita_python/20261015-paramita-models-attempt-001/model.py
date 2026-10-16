# Three sum: given a collection of integers, select a number of them that sum to zero.
# Each element is a Bool: selected or not. The count of selected elements is the
# instance field m, and the selected values must sum to zero.
from paramita.modelling import Bool


def build(instance):
    nums = instance["nums"]
    m = instance["m"]
    n = len(nums)

    # indices[i] = 1 if element i is selected
    sel = [Bool(f"sel_{i}") for i in range(n)]

    cons = []
    # exactly m elements are selected (m is read from the instance)
    cons.append(sum(sel) == m)
    # the selected elements sum to zero
    cons.append(sum(nums[i] * sel[i] for i in range(n)) == 0)

    return cons, {"indices": sel}
