# Bus driver scheduling: choose the fewest shifts such that every piece of work
# (task) is covered by exactly one chosen shift.
from pychoco.model import Model


def build(instance):
    num_work = instance["num_work"]  # number of tasks (pieces of work)
    num_shifts = instance["num_shifts"]  # number of candidate shifts
    shifts = instance["shifts"]  # shifts[i] = the tasks covered by shift i

    model = Model()

    # x[i] = 1 if shift i is selected
    x = [model.boolvar(name=f"x_{i}") for i in range(num_shifts)]

    # each task is covered by exactly one selected shift: among the shifts that
    # contain the task, exactly one is selected
    for t in range(num_work):
        covering_shifts = [x[i] for i in range(num_shifts) if t in shifts[i]]
        model.sum(covering_shifts, "=", 1).post()

    # minimise the number of shifts used (all shifts cost the same); the count is a
    # variable because Choco optimises a single variable
    n_selected = model.intvar(0, num_shifts, name="n_selected")
    model.sum(x, "=", n_selected).post()

    return model, {"x": x}, ("minimize", n_selected)
