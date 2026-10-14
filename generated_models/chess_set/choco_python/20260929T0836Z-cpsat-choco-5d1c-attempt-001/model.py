# Chess set: a joinery makes small and large boxwood chess sets. Decide how
# many of each to make in a week so that the lathe hours and the boxwood are not
# exceeded and the profit is as large as possible.
from pychoco.model import Model


def build(instance):
    # The problem statement fixes all the numbers; the instance carries no data.
    model = Model()

    # number of small and large sets made per week (at most 100 of each is ever useful)
    small_set = model.intvar(0, 100, name="small_set")
    large_set = model.intvar(0, 100, name="large_set")
    max_profit = model.intvar(0, 10000, name="max_profit")

    # boxwood: a small set needs 1 kg, a large one 3 kg, and only 200 kg is available
    model.scalar([small_set, large_set], [1, 3], "<=", 200).post()
    # lathe hours: 3 hours per small set, 2 per large set, 4 lathes x 40 hours = 160 hours
    model.scalar([small_set, large_set], [3, 2], "<=", 160).post()
    # profit: $5 per small set and $20 per large set
    model.scalar([small_set, large_set], [5, 20], "=", max_profit).post()

    # make as much profit as possible
    return model, {"small_set": small_set, "large_set": large_set, "max_profit": max_profit}, ("maximize", max_profit)
