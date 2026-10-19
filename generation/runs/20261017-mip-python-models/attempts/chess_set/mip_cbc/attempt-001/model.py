# Chess set production: a joinery makes small and large boxwood chess sets and
# wants to maximise weekly profit, subject to lathe hours and boxwood supply.
import mip


def build(instance):
    model = mip.Model(sense=mip.MAXIMIZE, solver_name="CBC")

    # Decision variables: number of small sets and number of large sets per week.
    small_set = model.add_var("small_set", lb=0, ub=200, var_type=mip.INTEGER)
    large_set = model.add_var("large_set", lb=0, ub=200, var_type=mip.INTEGER)

    # Output for the profit, tied to the sets by an equality row.
    max_profit = model.add_var("max_profit", lb=0, ub=10000, var_type=mip.INTEGER)

    # The small set requires 3 hours of machining on a lathe, and the large set requires 2 hours.
    # There are four lathes with skilled operators who each work a 40 hour week, so we have 160 lathe-hours per week.
    model.add_constr(mip.xsum([3 * small_set, 2 * large_set]) <= 160, name="lathe_hours")

    # The small chess set requires 1 kg of boxwood, and the large set requires 3 kg.
    # Unfortunately, boxwood is scarce and only 200 kg per week can be obtained.
    model.add_constr(mip.xsum([small_set, 3 * large_set]) <= 200, name="boxwood")

    # When sold, each of the large chess sets yields a profit of $20, and one of the small chess set has a profit of $5.
    # The problem is to decide how many sets of each kind should be made each week so as to maximize profit.
    model.add_constr(max_profit == mip.xsum([5 * small_set, 20 * large_set]), name="profit")

    model.objective = max_profit

    return model, {
        "small_set": small_set,
        "large_set": large_set,
        "max_profit": max_profit,
    }
