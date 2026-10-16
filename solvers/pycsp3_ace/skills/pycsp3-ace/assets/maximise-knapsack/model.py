"""0/1 knapsack: pick items of maximum total value within the capacity."""
from pycsp3 import *

values_ = [15, 10, 9, 5]       # "values" is a pycsp3 function: do not shadow it
weights = [1, 5, 3, 4]
capacity = 8
n = len(values_)

take = VarArray(size=n, dom={0, 1})

satisfy(
    # the chosen items must fit in the backpack
    Sum(weights[i] * take[i] for i in range(n)) <= capacity,
)
# maximise the total value of the chosen items
maximize(Sum(values_[i] * take[i] for i in range(n)))

status = solve()
if status is OPTIMUM:
    print("Objective:", bound())
    print("Take:", values(take))
elif status is SAT:
    print("Feasible, not proven optimal:", bound())
else:
    print("Status:", status)
