# Three sum: from a collection of integers, select exactly m elements whose sum is zero.
from exact import Exact


def build(instance):
    nums = instance["nums"]  # the collection of integers
    m = instance["m"]  # the number of elements that should sum to 0
    n = len(nums)

    solver = Exact()

    # indices[i] = 1 if element i is selected
    indices = [f"indices_{i}" for i in range(n)]
    for name in indices:
        solver.addVariable(name, 0, 1)

    # the selected elements sum to zero
    solver.addConstraint([(nums[i], indices[i]) for i in range(n) if nums[i]], True, 0, True, 0)

    # exactly m elements are selected
    solver.addConstraint([(1, name) for name in indices], True, m, True, m)

    return solver, {"indices": indices}
