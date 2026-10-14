# Bus driver scheduling: choose the fewest shifts from a given set so that every
# piece of work is covered by exactly one chosen shift.
import cpmpy as cp


def build(instance):
    num_work = instance["num_work"]        # number of pieces of work to cover
    shifts = instance["shifts"]            # shifts[i] lists the pieces of work shift i covers
    num_shifts = len(shifts)

    # x[i] is true when shift i is selected.
    x = cp.boolvar(shape=num_shifts, name="x")

    model = cp.Model()

    # Each piece of work is covered by exactly one selected shift (set partitioning).
    for t in range(num_work):
        covering = [x[i] for i in range(num_shifts) if t in shifts[i]]
        model += cp.sum(covering) == 1

    # Use as few shifts as possible (every shift costs the same).
    model.minimize(cp.sum(x))

    return model, {"x": x}
