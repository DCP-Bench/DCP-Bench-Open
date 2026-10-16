Alice has to give Bob some change -> the change must total the amount: m.scalar(coins, values, "=", amount)
She has different types of coins of different values -> coin values from instance field types_of_coins (scalar coefficients)
she has a certain number of coins of each value available -> coins[i] in 0..available_coins[i] (domain bounds)
How can the change be composed ... -> coin_counts[i] = number of coins of type i (decision variables)
minimizing the number of coins used -> total = m.sum(coins) (sum of coin_counts), MINIMIZE total
