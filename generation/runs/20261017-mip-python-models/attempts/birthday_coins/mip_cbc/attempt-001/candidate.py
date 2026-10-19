# Birthday coins: Tommy was given 15 coins (half-crowns, shillings and sixpence).
# Added up, the coins come to 1 pound 5 shillings 6 pence. How many half-crowns was he given?
# Money is counted in pence: a pound is 20 shillings, a shilling is 12 pence,
# a half-crown is 2 shillings and sixpence (30 pence), a sixpence is 6 pence.
import mip


def build(instance):
    model = mip.Model(solver_name="CBC")
    total_coins = 15
    total_pence = 1 * 20 * 12 + 5 * 12 + 6

    half_crowns = model.add_var("half_crowns", lb=0, ub=total_coins, var_type=mip.INTEGER)
    shillings = model.add_var("shillings", lb=0, ub=total_coins, var_type=mip.INTEGER)
    sixpences = model.add_var("sixpences", lb=0, ub=total_coins, var_type=mip.INTEGER)

    # Tommy was given 15 coins for his birthday
    model.add_constr(mip.xsum([half_crowns, shillings, sixpences]) == total_coins)

    # When he added it up, he found that he had 1 pound 5 shillings 6 pence
    model.add_constr(
        mip.xsum([30 * half_crowns, 12 * shillings, 6 * sixpences]) == total_pence
    )

    return model, {"half_crowns": half_crowns}
