# Bus driver scheduling: from a large set of possible shifts, each covering some
# pieces of work, pick the fewest shifts that cover every piece of work exactly once.
from ortools.sat.python import cp_model


def build(instance):
    num_work = instance["num_work"]  # pieces of work to cover
    shifts = instance["shifts"]  # shifts[i] = the pieces of work shift i covers

    model = cp_model.CpModel()

    # x[i] is true when shift i is selected
    x = [model.new_bool_var(f"x_{i}") for i in range(len(shifts))]

    # every piece of work is covered by exactly one selected shift (set partitioning)
    for work in range(num_work):
        model.add_exactly_one(x[i] for i, covered in enumerate(shifts) if work in covered)

    # use as few shifts as possible (all shifts cost the same)
    model.minimize(sum(x))

    return model, {"x": x}
