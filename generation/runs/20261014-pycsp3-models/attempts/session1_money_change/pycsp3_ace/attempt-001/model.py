# Problem: Pay the amount with the fewest coins, using no more than the available number of each coin type.
from pycsp3 import *

amount = data.amount
types = data.types_of_coins
available = data.available_coins
n = len(types)
# coin_counts[i] is the number of coins of value types[i] given to Bob
coin_counts = VarArray(size=n, dom=lambda i: range(available[i] + 1))
satisfy(
    # the coins given add up to the amount
    Sum(types[i] * coin_counts[i] for i in range(n)) == amount,
)
# minimize the number of coins used
minimize(Sum(coin_counts))
