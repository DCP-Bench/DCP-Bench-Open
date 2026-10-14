from pycsp3 import *

# Choose which dummies to knock over, so that the numbers on the knocked-down dummies
# add up to exactly the target sum.

values = data.values
target = data.target_sum
n = len(values)

# dummies[i] is 1 when dummy i is knocked over, 0 otherwise
dummies = VarArray(size=n, dom={0, 1})

satisfy(
    # the numbers on the dummies that are knocked over add up to exactly the target sum
    Sum(values[i] * dummies[i] for i in range(n)) == target,
)
