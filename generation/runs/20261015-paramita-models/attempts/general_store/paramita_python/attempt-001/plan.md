# Plan: general_store (attempt-001)

Each letter is one digit (one-hot, x_L_d); the ten letters take ten different digits (permutation).
Column addition, right to left, with carries (unary carry bits, c_j >= i).

- "Each different letter stands for a different digit" -> sum_d x_L_d == 1 per letter; sum_L x_L_d == 1 per digit
- leading zeros: the statement sets no rule; no ~x_L_0 constraint (with it the puzzle is UNSAT, checked on the encoding)
- "words above the line add to the total ALL WOOL" -> per column j: sum(letter values in column j) + carry_in == value(result letter) + 10 * carry_out, carry_out of column 6 = 0
- carry_j bounded by (9 * digits in column + carry_in) / 10 (derived) -> unary bits, If(bit_{i+1}, bit_i)
- objective: none (satisfaction); outputs = integer value of each letter (PB sum d * x_L_d)
