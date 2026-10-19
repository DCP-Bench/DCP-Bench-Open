"""Make change for 63 with the fewest coins of values 1, 5, 10, 25."""
from pycsp3 import *

coins = [1, 5, 10, 25]
amount = 63

# count[c] is how many coins of value coins[c] are used
count = VarArray(size=len(coins), dom=range(amount + 1))

satisfy(
    # the coins add up to the amount
    Sum(coins[c] * count[c] for c in range(len(coins))) == amount,
)
# use as few coins as possible
minimize(Sum(count))

status = solve(options="-t=10s")    # ACE time limit
if status is OPTIMUM:
    print("Objective:", bound())
    print("Counts:", values(count))
else:
    print("Status:", status)
