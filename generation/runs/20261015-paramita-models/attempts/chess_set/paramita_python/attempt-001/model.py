# Chess sets: a joinery makes two sizes of boxwood chess sets each week.
# Choose how many small and large sets to make, within lathe hours and boxwood,
# so as to maximise profit.
# The constants are the problem's own (4 lathes x 40 hours, 200 kg boxwood,
# machining hours, boxwood use and profits); the problem has no instance fields.
from paramita.modelling import Bool, If

LATHE_HOURS = 4 * 40  # four lathes, 40 hours each per week
BOXWOOD_KG = 200  # boxwood available per week
SMALL_LATHE_H, LARGE_LATHE_H = 3, 2  # machining hours per set
SMALL_WOOD_KG, LARGE_WOOD_KG = 1, 3  # boxwood per set
SMALL_PROFIT, LARGE_PROFIT = 5, 20  # profit per set


def unary_count(name, ub):
    # ge[k] is true when the count is at least k+1 (order encoding)
    ge = [Bool(f"{name}_ge_{k + 1}") for k in range(ub)]
    cons = [If(ge[k + 1], ge[k]) for k in range(ub - 1)]
    return ge, cons


def build(instance):
    # the most sets of each kind that the lathe hours and the boxwood would allow alone
    small_max = min(LATHE_HOURS // SMALL_LATHE_H, BOXWOOD_KG // SMALL_WOOD_KG)
    large_max = min(LATHE_HOURS // LARGE_LATHE_H, BOXWOOD_KG // LARGE_WOOD_KG)

    small_ge, cons = unary_count("small", small_max)
    large_ge, cons_large = unary_count("large", large_max)
    cons += cons_large
    small = sum(small_ge)  # number of small sets made
    large = sum(large_ge)  # number of large sets made

    # the lathe hours used by both sets must not exceed the lathe hours available
    cons.append(SMALL_LATHE_H * small + LARGE_LATHE_H * large <= LATHE_HOURS)
    # the boxwood used by both sets must not exceed the boxwood available
    cons.append(SMALL_WOOD_KG * small + LARGE_WOOD_KG * large <= BOXWOOD_KG)

    # the profit from the sets made, to be maximised
    profit = SMALL_PROFIT * small + LARGE_PROFIT * large
    return cons, {"small_set": small, "large_set": large, "max_profit": profit}, ("maximize", profit)
