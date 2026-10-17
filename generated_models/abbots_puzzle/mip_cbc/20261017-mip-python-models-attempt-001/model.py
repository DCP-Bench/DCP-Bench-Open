# Abbot's puzzle: 100 bushels of corn are distributed among 100 people such that
# each man receives three bushels, each woman two, and each child half a bushel,
# and there are five times as many women as men. Find the number of men, women and children.
import mip


def build(instance):
    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")
    men = model.add_var("men", lb=0, ub=100, var_type=mip.INTEGER)
    women = model.add_var("women", lb=0, ub=100, var_type=mip.INTEGER)
    children = model.add_var("children", lb=0, ub=100, var_type=mip.INTEGER)

    # 100 people in total
    model.add_constr(men + women + children == 100)

    # 100 bushels: each man 3, each woman 2, each child 1/2 (both sides doubled to stay integer)
    model.add_constr(6 * men + 4 * women + children == 200)

    # five times as many women as men
    model.add_constr(women == 5 * men)

    return model, {"men": men, "women": women, "children": children}
