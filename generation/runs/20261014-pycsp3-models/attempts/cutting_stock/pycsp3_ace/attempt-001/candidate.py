from pycsp3 import *

# Cutting stock: raw rolls of width roll_width are cut with a set of patterns. Pattern p
# cuts num_rolls_width[p][j] pieces of width widths[j]. The orders must be met.

roll_width = data.roll_width
widths = data.widths
orders = data.orders
pattern = data.num_rolls_width
num_patterns = data.num_patterns

# patterns_used[p] is the number of rolls cut with pattern p
patterns_used = VarArray(size=num_patterns, dom=range(0, max(orders) + 1))
# min_rolls_cut is the total number of raw rolls cut
min_rolls_cut = Var(dom=range(0, sum(orders) + 1))

satisfy(
    # the total number of rolls cut is the sum over the patterns
    min_rolls_cut == Sum(patterns_used),

    # for each width, the pieces cut from all rolls meet the number of orders
    [Sum(pattern[p][j] * patterns_used[p] for p in range(num_patterns)) >= orders[j]
     for j in range(len(widths))],
)

# minimise the total number of raw rolls cut
minimize(min_rolls_cut)
