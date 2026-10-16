Alice has to give Bob some change -> payment: sum over coin types of type_value * count == amount
She has different types of coins of different values -> types_of_coins[k] = value of type k
she has a certain number of coins of each value available -> count_k <= available_coins[k]: unary bits u[k][1..available_k], If(u[k][j+1], u[k][j]), count_k = sum of its bits
How can the change be composed with the available coins -> PB: sum(types[k] * u[k][j]) == amount
minimizing the number of coins used -> objective minimize sum of all count_k bits (unary bits)
Print the number of coins of each type to give to Bob (coin_counts) -> output coin_counts[k] = count_k integer expression
