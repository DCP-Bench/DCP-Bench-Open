from pycsp3 import *

# Progress City bus schedule: the day is split into 4-hour intervals, and the
# demand for buses in each interval is given. Each bus works 8 successive hours,
# that is 2 intervals, and the day wraps around from the last interval to the first.

demands = data.demands
n = len(demands)

# x[i] is the number of buses that start in interval i
x = VarArray(size=n, dom=range(0, max(demands) + 1))

satisfy(
    # the buses available in each interval meet the demand for that interval
    [x[i] + x[(i - 1) % n] >= demands[i] for i in range(n)]
)

# minimise the total number of buses
minimize(Sum(x))
