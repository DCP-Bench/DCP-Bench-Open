Each new term is the sum of the previous two, starting with 1 and 2 -> terms t_1..t_32 as binary integers (22 bits each), t_1 = 1, t_2 = 2, t_{i+2} == t_i + t_{i+1} as PB over the bits
Horizon: F_33 = 5702887 > 4000000 and the terms increase from t_3 on, so t_1..t_32 hold every term not exceeding four million -> fixed count of 32 (problem bound, no instance field)
Sum of all the even-valued terms which do not exceed four million -> per term i and bit k >= 1, g_{i,k} <-> (bit_{i,k} & ~bit_{i,0}) (even term contributes its bits), res = sum of 2^k * g_{i,k}
Objective: none (the output res is the sum; satisfaction)
