# Dinner problem: choose how many grandparents (1-6), parents (1-10) and children
# (1-40) go to dinner. There must be 20 people in total and the dinner must cost $20.
# Grandparents cost $3, parents $2 and children $0.50. Output the counts as
# (grandparents, parents, children).
import mip


def build(instance):
    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # We're going out to dinner taking 1-6 grandparents, 1-10 parents and/or 1-40 children
    grandparents = model.add_var("grandparents", lb=1, ub=6, var_type=mip.INTEGER)
    parents = model.add_var("parents", lb=1, ub=10, var_type=mip.INTEGER)
    children = model.add_var("children", lb=1, ub=40, var_type=mip.INTEGER)

    # There must be 20 total people at dinner
    model += mip.xsum([grandparents, parents, children]) == 20

    # and it must cost $20. Costs are doubled to keep coefficients integer:
    # grandparents $3 -> 6, parents $2 -> 4, children $0.50 -> 1, total 40
    model += mip.xsum([6 * grandparents, 4 * parents, children]) == 40

    return model, {
        "grandparents": grandparents,
        "parents": parents,
        "children": children,
    }
