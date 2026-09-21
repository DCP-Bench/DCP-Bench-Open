# Fewest raw rolls cut, using the given patterns to meet every order.
#
# The instance also carries roll_width and the widths themselves. The reference
# uses neither in a constraint, only len(widths): the patterns in
# num_rolls_width already encode what fits on a roll.
from dcp_pb import Pb


def build(instance):
    orders = instance["orders"]
    num_patterns = instance["num_patterns"]
    per_pattern = instance["num_rolls_width"]
    widths = len(instance["widths"])

    # 0..100 uses of each pattern is the bound the reference declares.
    pb = Pb()
    used = pb.ints(num_patterns, 0, 100)
    for i in range(widths):
        pb.ge([(per_pattern[j][i], used[j]) for j in range(num_patterns)], orders[i])

    rolls = pb.int(0, 100 * num_patterns)
    pb.eq([(1, u) for u in used] + [(-1, rolls)], 0)
    pb.minimise([(1, rolls)])
    return pb, {"patterns_used": used, "min_rolls_cut": rolls}
