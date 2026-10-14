# Chess set: a joinery makes small and large boxwood chess sets. Decide how
# many of each to make in a week so that the lathe hours and the boxwood are not
# exceeded and the profit is as large as possible.
from hermax.model import Model


def build(instance):
    # The problem statement fixes all the numbers; the instance carries no data.
    m = Model()
    # number of small and large sets made per week (at most 100 of each is ever useful)
    small_set = m.int("small_set", 0, 100)
    large_set = m.int("large_set", 0, 100)

    # boxwood: a small set needs 1 kg, a large one 3 kg, and only 200 kg is available
    m &= (small_set + 3 * large_set <= 200)
    # lathe hours: 3 hours per small set, 2 per large set, 4 lathes x 40 hours = 160 hours
    m &= (3 * small_set + 2 * large_set <= 160)

    # Maximise the profit, $5 per small set and $20 per large set: a set that is not
    # made (small_set < k) costs its profit, so the soft clause is the literal itself.
    for k in range(1, 101):
        m.obj[5] += (small_set >= k)
        m.obj[20] += (large_set >= k)

    # max_profit is a declared output: the profit as a sum of scaled integers; its
    # largest possible value is 5 * 100 + 20 * 100
    max_profit = m.sum_var([m.scale(small_set, 5), m.scale(large_set, 20)])

    return m, {"small_set": small_set, "large_set": large_set, "max_profit": max_profit}
