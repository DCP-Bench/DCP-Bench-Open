# Bus driver scheduling (CSPLib prob022): choose a set of shifts so that every
# piece of work is covered by exactly one chosen shift, using as few shifts as
# possible. Each shift is a set of pieces of work, given in the instance.
from paramita.modelling import Bool


def build(instance):
    shifts = instance["shifts"]
    num_work = instance["num_work"]

    # x[s] is true when shift s is selected
    x = [Bool(f"x_{s}") for s in range(len(shifts))]

    # the shifts that contain each piece of work
    covering = [[] for _ in range(num_work)]
    for s, tasks in enumerate(shifts):
        for w in tasks:
            covering[w].append(x[s])

    cons = []
    # every piece of work is covered by exactly one selected shift
    for w in range(num_work):
        cons.append(sum(covering[w]) == 1)

    # minimise the number of selected shifts (all shifts cost the same)
    total = sum(x)
    return cons, {"x": x}, ("minimize", total)
