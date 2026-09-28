"""Four numbers: find three integers in 1..10 from whose subset sums every given number can be made."""
from docplex.mp.model import Model

# The three numbers to find each lie in 1..10, as the problem states.
LOW, HIGH = 1, 10
PARTS = range(3)


def build(instance):
    numbers = instance["numbers"]
    targets = range(len(numbers))

    model = Model("four_numbers")

    # x[j] is the j-th of the three numbers.
    x = model.integer_var_list(len(PARTS), LOW, HIGH, name="x")

    # uses[i, j] is 1 when x[j] is part of the subset that sums to numbers[i].
    uses = model.binary_var_matrix(targets, PARTS, name="uses")

    # part[i, j] is uses[i, j] * x[j]. CPLEX refuses a product of two variables
    # as non-convex, so it is written linearly: part is 0 when uses is 0, and
    # equals x[j] when uses is 1, using the bounds 1..10 of x.
    part = model.integer_var_matrix(targets, PARTS, 0, HIGH, name="part")
    for i in targets:
        for j in PARTS:
            model.add_constraint(part[i, j] <= HIGH * uses[i, j], ctname=f"off_high_{i}_{j}")
            model.add_constraint(part[i, j] >= LOW * uses[i, j], ctname=f"off_low_{i}_{j}")
            model.add_constraint(part[i, j] <= x[j] - LOW * (1 - uses[i, j]), ctname=f"on_high_{i}_{j}")
            model.add_constraint(part[i, j] >= x[j] - HIGH * (1 - uses[i, j]), ctname=f"on_low_{i}_{j}")

    # Each given number is the sum of its subset of the three.
    for i in targets:
        model.add_constraint(model.sum(part[i, j] for j in PARTS) == numbers[i], ctname=f"sum_{i}")

    return model, {"x": x}
