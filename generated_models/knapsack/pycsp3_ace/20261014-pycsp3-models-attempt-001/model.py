from pycsp3 import *

# 0/1 knapsack: a hiker chooses items with a value and a weight, and the chosen items
# must not weigh more than the capacity of the backpack.

values = data.values
weights = data.weights
capacity = data.capacity
n_items = len(values)

# x[i] is 1 when item i is taken
x = VarArray(size=n_items, dom={0, 1})

satisfy(
    # the items taken weigh no more than the capacity of the backpack
    Sum(weights[i] * x[i] for i in range(n_items)) <= capacity,
)

# maximise the total value of the items taken
maximize(Sum(values[i] * x[i] for i in range(n_items)))
