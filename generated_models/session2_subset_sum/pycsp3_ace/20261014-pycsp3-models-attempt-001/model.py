# Coin bags: choose how many bags of each type were stolen so that the stolen bags hold exactly the total number of coins lost.
from pycsp3 import *

coin_numbers = data.coin_numbers
total_coins_lost = data.total_coins_lost
num_types = len(coin_numbers)

# bags[t] = number of bags of coin type t that were stolen
bags = VarArray(size=num_types, dom=range(total_coins_lost + 1))

satisfy(
    # the stolen bags contain exactly the coins that were lost
    Sum(bags[t] * coin_numbers[t] for t in range(num_types)) == total_coins_lost,
)
