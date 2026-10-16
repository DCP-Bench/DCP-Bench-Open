# crypta plan (attempt-001)

Letters A..J are distinct digits 0..9 (allDifferent over all ten).
Numbers are 20 digits each; the first letter of each number is nonzero: B (first addend), D (second addend), G (sum).
Column addition from the least significant digit: digit_a + digit_b + carry_in = digit_s + 10 * carry_out, carry_in of column 0 is 0, carry_out of the last column is 0.
- "B A I J ... E A + D H F G ... J E = G J E G ... E F" -> column equations (20 columns, carries as 0..1 variables)
- Objective: none (satisfaction). Outputs: A..J.
