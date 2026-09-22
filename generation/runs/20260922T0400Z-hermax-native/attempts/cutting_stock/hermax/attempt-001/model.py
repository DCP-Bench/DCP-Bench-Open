# Fewest raw rolls cut, using the given patterns to meet every order.
#
# The instance also carries roll_width and the widths themselves. The reference
# uses neither in a constraint, only len(widths): the patterns already encode
# what fits on a roll.
from hermax.model import Model


def build(instance):
    orders = instance["orders"]
    num_patterns = instance["num_patterns"]
    per_pattern = instance["num_rolls_width"]
    widths = len(instance["widths"])

    # A pattern never needs more uses than the largest order it can serve.
    ceiling = max(orders)
    m = Model()
    used = m.int_vector("patterns_used", num_patterns, 0, ceiling)
    for i in range(widths):
        m &= (sum(per_pattern[j][i] * used[j] for j in range(num_patterns)) >= orders[i])

    rolls = m.sum_var(list(used), name="min_rolls_cut")
    m.obj += rolls
    return m, {"patterns_used": used, "min_rolls_cut": rolls}
