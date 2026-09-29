# Chess set: a joinery makes small and large boxwood chess sets. Decide how
# many of each to make in a week so that the lathe hours and the boxwood are not
# exceeded and the profit is as large as possible.
import z3


def build(instance):
    # The problem statement fixes all the numbers; the instance carries no data.
    solver = z3.Solver()

    # number of small and large sets made per week (at most 100 of each is ever useful)
    small_set, large_set, max_profit = z3.Ints("small_set large_set max_profit")
    solver.add(small_set >= 0, small_set <= 100, large_set >= 0, large_set <= 100)

    # boxwood: a small set needs 1 kg, a large one 3 kg, and only 200 kg is available
    solver.add(small_set + 3 * large_set <= 200)
    # lathe hours: 3 hours per small set, 2 per large set, 4 lathes x 40 hours = 160 hours
    solver.add(3 * small_set + 2 * large_set <= 160)
    # profit: $5 per small set and $20 per large set
    solver.add(max_profit == 5 * small_set + 20 * large_set)

    # make as much profit as possible
    return solver, {"small_set": small_set, "large_set": large_set, "max_profit": max_profit}, ("maximize", max_profit)
