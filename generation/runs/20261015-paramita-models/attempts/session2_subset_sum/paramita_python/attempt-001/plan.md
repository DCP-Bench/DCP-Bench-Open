A bank van had several bags of coins, each containing a number of coins from a given list -> for each bag type i, x_i = number of bags of type i stolen, one-hot over 0..total//coin_numbers[i] (`xv[i][k]`, `sum(xv[i].values()) == 1`), value `x_i = sum(k * xv[i][k])`
there are multiple bags of the same kind -> no upper limit on x_i beyond what the total allows, so the domain is 0..total//c_i
A total of a given number of coins were lost -> `sum(c_i * x_i) == total_coins_lost` as one PB constraint over the one-hot Bools (weights c_i*k, all at most total)
find how many bags were stolen for each type of coin bag -> output `bags[i] = x_i` (integer expression)
objective -> none (satisfaction)
