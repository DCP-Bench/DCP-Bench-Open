# Dinner: a family goes out to dinner with 1-6 grandparents, 1-10 parents and
# 1-40 children; 20 people in all must cost exactly $20. How many of each?
import z3


def build(instance):
    del instance  # the puzzle states its own prices and head counts

    grandparents, parents, children = z3.Ints("grandparents parents children")

    solver = z3.Solver()

    # "1-6 grandparents, 1-10 parents and/or 1-40 children".
    solver.add(grandparents >= 1, grandparents <= 6)
    solver.add(parents >= 1, parents <= 10)
    solver.add(children >= 1, children <= 40)

    # Grandparents cost $3, parents $2 and children $0.50; the bill is $20. Prices
    # are doubled (6, 4, 1 against 40) to keep everything in whole numbers.
    solver.add(6 * grandparents + 4 * parents + 1 * children == 20 * 2)

    # There are 20 people at dinner.
    solver.add(grandparents + parents + children == 20)

    return solver, {"grandparents": grandparents, "parents": parents, "children": children}
