sequence of n bits, each +1 or -1 -> Booleans b[i] (1 = +1, 0 = -1), output s[i] = 2*b[i] - 1 as IntVar
the bits are the decisions; the output and all auxiliaries follow from them
product of two bits is +1 when equal and -1 when different -> d[i][k] = b[i] xor b[(i+k) mod n] (rel BOT_XOR)
periodic autocorrelation C_k = sum_i S_i S_(i+k mod n) = n - 2 * sum_i d[i][k] -> linear over d with coefficients -2 and C_k with coefficient 1 = n
energy = sum_{k=1..n-1} C_k^2 -> sq_k = sqr(C_k), total = sum sq_k
minimise the energy -> minimize(total)
branching -> BOOL_VAR_NONE, BOOL_VAL_MIN on b, restarts not needed for the first run
