# Five Spanish brigands (Alfonso A, Benito B, Carlos C, Diego D, Esteban E) count
# their spoils: together they hold exactly 200 doubloons, and no brigand has less
# than one doubloon. Find the number of doubloons each may have.
import mip


def build(instance):
    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # no brigand had less than one doubloon
    A = model.add_var("A", lb=1, ub=200, var_type=mip.INTEGER)
    B = model.add_var("B", lb=1, ub=200, var_type=mip.INTEGER)
    C = model.add_var("C", lb=1, ub=200, var_type=mip.INTEGER)
    D = model.add_var("D", lb=1, ub=200, var_type=mip.INTEGER)
    E = model.add_var("E", lb=1, ub=200, var_type=mip.INTEGER)

    # they had altogether exactly 200 doubloons
    model.add_constr(mip.xsum([A, B, C, D, E]) == 200)

    # if Alfonso had twelve times as much, Benito three times as much, Carlos the same
    # amount, Diego half as much, and Esteban one-third as much, they would still have
    # altogether just 200 doubloons (multiplied by 6 to stay in integers)
    model.add_constr(
        mip.xsum([72 * A, 18 * B, 6 * C, 3 * D, 2 * E]) == 1200
    )

    outputs = {"A": A, "B": B, "C": C, "D": D, "E": E}
    return model, outputs
