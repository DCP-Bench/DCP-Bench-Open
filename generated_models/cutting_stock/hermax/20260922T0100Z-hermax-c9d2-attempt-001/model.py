# Fewest raw rolls cut, using the given patterns to meet every order.
#
# The instance also carries roll_width and the widths themselves. The reference
# uses neither in a constraint, only len(widths): the patterns already encode
# what fits on a roll.
from dcp_maxsat import MaxSat


def build(instance):
    orders = instance["orders"]
    num_patterns = instance["num_patterns"]
    per_pattern = instance["num_rolls_width"]
    widths = len(instance["widths"])

    # A pattern never needs more uses than the largest order it can serve.
    ceiling = max(orders)
    sat = MaxSat()
    used = sat.ints(num_patterns, 0, ceiling)
    for i in range(widths):
        yields_i = [per_pattern[j][i] for j in range(num_patterns)]
        sat.weighted_sum_ge(yields_i, used, orders[i])

    rolls = sat.int(0, ceiling * num_patterns)
    sat.link_sum([(1, u) for u in used], rolls)
    return sat, {"patterns_used": used, "min_rolls_cut": rolls}, ("minimize", rolls)
