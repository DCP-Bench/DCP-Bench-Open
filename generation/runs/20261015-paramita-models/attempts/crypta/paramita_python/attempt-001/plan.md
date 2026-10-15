Each letter A..J is a digit 0..9 -> one-hot Bools x[L][v], sum over v == 1 -> value expression sum(v * x[L][v])
all letters distinct -> per digit v: sum over letters x[L][v] == 1 (10 letters, 10 digits)
first letter of each number cannot be zero -> ~x[B][0], ~x[D][0], ~x[G][0]
column-wise addition, 20 columns from the right: digit(L1) + digit(L2) + carry_in == digit(R) + 10 * carry_out -> PB over one-hot value expressions and carry Bools
carry into the rightmost column is 0; carry out of the leftmost column is 0 (result has the same length)
objective -> none (satisfaction)
