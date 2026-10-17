# csplib_022 bus driver scheduling: choose a subset of shifts so that each piece of work
# is covered exactly once, minimising the number of shifts selected. Output x[j] = 1 when
# shift j is selected.
import mip


def build(instance):
    num_work = instance["num_work"]
    shifts = instance["shifts"]
    num_shifts = len(shifts)

    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    x = [model.add_var(f"x_{j}", var_type=mip.BINARY) for j in range(num_shifts)]

    # each piece of work is covered exactly once by the selected shifts
    covers = [[] for _ in range(num_work)]
    for j, shift in enumerate(shifts):
        for w in shift:
            covers[w].append(j)
    for w in range(num_work):
        model += mip.xsum(x[j] for j in covers[w]) == 1

    # the cost of each shift is equal: minimise the number of shifts selected
    model.objective = mip.xsum(x)

    return model, {"x": x}
