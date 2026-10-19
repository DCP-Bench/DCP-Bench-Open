# Schedule 4 people into 4 interview slots based on their free-busy schedules.
# m[i][j] = 1 when person i is free in slot j. x[i][j] = True when person i
# is assigned to slot j. Output x is a list of lists of booleans (declared [4][4]bool).
import mip


def build(instance):
    free = instance["m"]
    people = len(free)
    slots = len(free[0])
    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    x = [
        [model.add_var(name=f"x_{i}_{j}", var_type=mip.BINARY) for j in range(slots)]
        for i in range(people)
    ]

    # Each person is assigned to exactly one slot.
    for i in range(people):
        model += mip.xsum(x[i][j] for j in range(slots)) == 1

    # Each slot takes at most one person.
    for j in range(slots):
        model += mip.xsum(x[i][j] for i in range(people)) <= 1

    # A person is only assigned to a slot in which that person is free.
    for i in range(people):
        for j in range(slots):
            model += x[i][j] <= free[i][j]

    return model, {"x": x}
