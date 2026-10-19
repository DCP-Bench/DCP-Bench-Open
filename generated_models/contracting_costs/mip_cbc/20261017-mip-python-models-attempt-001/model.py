# Contracting costs: a contractor planning the construction of a house would have to pay
# $1,100 to the paper hanger and the painter, $1,700 to the painter and plumber,
# $1,100 to the plumber and electrician, $3,300 to the electrician and carpenter,
# $5,300 to the carpenter and mason, and $3,200 to the mason and painter.
# What does each man charge for his services? Satisfaction problem with a unique solution.
import mip


def build(instance):
    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # Charges are nonnegative amounts in dollars, and no single charge can exceed the
    # largest sum paid to a pair (5,300), so that is the upper bound.
    upper = 5300
    paper_hanger = model.add_var("paper_hanger", lb=0, ub=upper, var_type=mip.INTEGER)
    painter = model.add_var("painter", lb=0, ub=upper, var_type=mip.INTEGER)
    plumber = model.add_var("plumber", lb=0, ub=upper, var_type=mip.INTEGER)
    electrician = model.add_var("electrician", lb=0, ub=upper, var_type=mip.INTEGER)
    carpenter = model.add_var("carpenter", lb=0, ub=upper, var_type=mip.INTEGER)
    mason = model.add_var("mason", lb=0, ub=upper, var_type=mip.INTEGER)

    # $ 1,100 to the paper hanger and the painter,
    model.add_constr(mip.xsum([paper_hanger, painter]) == 1100)

    # $ 1,700 to the painter and plumber,
    model.add_constr(mip.xsum([painter, plumber]) == 1700)

    # $ 1,100 to the plumber and electrician,
    model.add_constr(mip.xsum([plumber, electrician]) == 1100)

    # $ 3,300 to the electrician and carpenter,
    model.add_constr(mip.xsum([electrician, carpenter]) == 3300)

    # $ 5,300 to the carpenter and mason,
    model.add_constr(mip.xsum([carpenter, mason]) == 5300)

    # $ 3,200 to the mason and painter.
    model.add_constr(mip.xsum([mason, painter]) == 3200)

    outputs = {
        "carpenter": carpenter,
        "electrician": electrician,
        "mason": mason,
        "painter": painter,
        "paper_hanger": paper_hanger,
        "plumber": plumber,
    }
    return model, outputs
