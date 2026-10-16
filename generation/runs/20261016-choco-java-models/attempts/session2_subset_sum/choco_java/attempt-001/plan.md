A bank van had several bags of coins, each containing a number of coins from a given list -> coin_numbers[i] is the coin count of bag type i (instance field)
(there are multiple bags of the same kind) -> bags[i] is a nonnegative integer count with no fixed availability
thieves stole some bags -> bags[i] = number of bags stolen of type i
A total of a given number of coins were lost -> m.scalar(bags, coin_numbers, "=", total_coins_lost)
find how many bags were stolen for each type -> output bags; satisfaction, no objective
