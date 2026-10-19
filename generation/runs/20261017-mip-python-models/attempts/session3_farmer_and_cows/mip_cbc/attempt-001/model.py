# Farmer and cows: a farmer has num_cows cows, cow i (1..num_cows) gives i units of milk.
# He has num_sons sons and wants to give each son a given number of cows (cows_per_son),
# so that the total milk per son is the same for every son.
# Output cow_assignments[c] is the 0-based son that cow c+1 goes to.
import mip


def build(instance):
    num_cows = instance["num_cows"]
    num_sons = instance["num_sons"]
    cows_per_son = instance["cows_per_son"]

    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # x[c][s] = 1 when cow c (0-based) goes to son s
    x = [[model.add_var(f"x_{c}_{s}", var_type=mip.BINARY) for s in range(num_sons)]
         for c in range(num_cows)]

    # The farmer wants to distribute his cows to them according to a given distribution.
    # Each cow is given to exactly one son.
    for c in range(num_cows):
        model.add_constr(mip.xsum(x[c][s] for s in range(num_sons)) == 1)

    # Each son receives the number of cows given by the distribution.
    for s in range(num_sons):
        model.add_constr(mip.xsum(x[c][s] for c in range(num_cows)) == cows_per_son[s])

    # The total quantity of milk produced should be the same for each son.
    # Cow numbered c + 1 gives milk c + 1. Each son's milk equals the milk of son 0.
    milk = [mip.xsum((c + 1) * x[c][s] for c in range(num_cows)) for s in range(num_sons)]
    for s in range(1, num_sons):
        model.add_constr(milk[s] == milk[0])

    # Output: the son of each cow, as an integer tied to its binaries.
    assignment = []
    for c in range(num_cows):
        a = model.add_var(f"son_{c}", lb=0, ub=num_sons - 1, var_type=mip.INTEGER)
        model.add_constr(a == mip.xsum(s * x[c][s] for s in range(num_sons)))
        assignment.append(a)

    return model, {"cow_assignments": assignment}
