# Farmer and cows: cow k gives k units of milk. Distribute the cows among the sons so that each son
# gets the given number of cows and all sons get the same total amount of milk.
from exact import Exact


def build(instance):
    num_cows = instance["num_cows"]
    num_sons = instance["num_sons"]
    cows_per_son = instance["cows_per_son"]  # number of cows each son must get

    # cow i (0-based) gives i + 1 units of milk; every son gets an equal share of the total
    milk_per_cow = list(range(1, num_cows + 1))
    total_milk = sum(milk_per_cow)
    total_milk_per_son = total_milk // num_sons

    solver = Exact()

    # cow_assignments[i] = the son (0..num_sons-1) who gets cow i
    cow_assignments = [f"cow_{i}" for i in range(num_cows)]
    for name in cow_assignments:
        solver.addVariable(name, 0, num_sons - 1)

    # gets[i][s] = 1 when cow i goes to son s. Counting the cows and the milk of a son needs to
    # talk about the value of cow_assignments[i], so each cow gets one 0/1 variable per son
    # (num_sons is small), tied to cow_assignments[i] by a channelling constraint.
    gets = [[f"gets_{i}_{s}" for s in range(num_sons)] for i in range(num_cows)]
    for i in range(num_cows):
        for s in range(num_sons):
            solver.addVariable(gets[i][s], 0, 1)
        solver.addConstraint([(1, gets[i][s]) for s in range(num_sons)], True, 1, True, 1)
        solver.addConstraint([(s, gets[i][s]) for s in range(1, num_sons)]
                             + [(-1, cow_assignments[i])], True, 0, True, 0)

    for s in range(num_sons):
        # each son gets a specific number of cows
        solver.addConstraint([(1, gets[i][s]) for i in range(num_cows)],
                             True, cows_per_son[s], True, cows_per_son[s])
        # the total milk production is the same for each son
        solver.addConstraint([(milk_per_cow[i], gets[i][s]) for i in range(num_cows)],
                             True, total_milk_per_son, True, total_milk_per_son)

    return solver, {"cow_assignments": cow_assignments}
