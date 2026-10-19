# Bananas: buy 100 fruits for exactly 100 dollars, buying every type at least once,
# minimising the number of bananas and apples.
# Prices: 5 bananas cost 3 dollars, 7 oranges cost 5, 9 mangoes cost 7, 3 apples cost 9.
# Unit prices are multiplied by 315 (the lcm of 5, 7, 9 and 3) to keep every coefficient integral.
import mip


def build(instance):
    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    bananas = model.add_var("bananas", lb=1, ub=100, var_type=mip.INTEGER)
    oranges = model.add_var("oranges", lb=1, ub=100, var_type=mip.INTEGER)
    mangoes = model.add_var("mangoes", lb=1, ub=100, var_type=mip.INTEGER)
    apples = model.add_var("apples", lb=1, ub=100, var_type=mip.INTEGER)

    # I need to purchase 100 fruits in total.
    model.add_constr(mip.xsum([bananas, oranges, mangoes, apples]) == 100, "total_fruits")

    # I need to spend 100 dollars.
    # Scaled by 315: banana 189, orange 225, mango 245, apple 945, budget 31500.
    model.add_constr(
        mip.xsum([189 * bananas, 225 * oranges, 245 * mangoes, 945 * apples]) == 31500,
        "total_cost",
    )

    # I do not like bananas and apples, so these should be of minimum quantity.
    model.objective = mip.xsum([bananas, apples])

    return model, {
        "bananas": bananas,
        "oranges": oranges,
        "mangoes": mangoes,
        "apples": apples,
    }
