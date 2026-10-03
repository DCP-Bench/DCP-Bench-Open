# Bus driver scheduling: choose as few shifts as possible from a given pool so
# that every piece of work is covered by exactly one chosen shift.
from hermax.model import Model


def build(instance):
    num_work = instance["num_work"]  # pieces of work to cover
    shifts = instance["shifts"]  # shifts[i] = the pieces of work shift i covers
    num_shifts = len(shifts)

    m = Model()
    # x[i] = shift i is selected
    x = m.bool_vector("x", num_shifts)

    # every piece of work is covered by exactly one selected shift
    for t in range(num_work):
        covering = [x[i] for i in range(num_shifts) if t in shifts[i]]
        m &= (sum(covering) == 1)

    # Minimise the number of selected shifts. A soft clause pays when its
    # literal is false, so the cost of selecting a shift is stated on ~x[i]:
    # each selected shift breaks one clause of weight 1.
    for i in range(num_shifts):
        m.obj[1] += ~x[i]

    return m, {"x": x}
