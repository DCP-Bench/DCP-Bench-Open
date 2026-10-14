# Plan: session2_subset_sum (satisfaction)

- "a number of bags stolen for each type of coin bag" -> one IntVar bags[i] per bag type, domain 0..total (declared by IntVarArray), tightened below
- "each bag type contains a number of coins from the list": bags stolen of type i hold coin_numbers[i] coins each -> bags[i] <= total / coin_numbers[i] -> rel(*this, bags[i], IRT_LQ, total / c_i)
- "a total of a given number of coins were lost" -> sum of coin_numbers[i] * bags[i] equals total_coins_lost -> linear(*this, IntArgs(coins), bags, IRT_EQ, total)
- branching: bags in order, smallest domain first (INT_VAR_SIZE_MIN), smallest value first (INT_VAL_MIN); the linear constraint fixes the rest
- objective: none (satisfaction); outputs: bags
