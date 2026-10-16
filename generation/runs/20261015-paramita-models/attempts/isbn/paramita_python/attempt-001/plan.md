# ISBN-13 validation and check digit
Digit at each of the 13 positions: one-hot over 0..9 (`d_i_v`), given digits forced by unit constraints.
- The number starts with 978 or 979 -> digit 0 = 9, digit 1 = 7, digit 2 in {8, 9} -> one-hot unit / exactly-one over {8,9}.
- Multiply the first 12 digits alternately by 1 and 3 (starting with 1), sum the products -> PB sum of (weight * one-hot digit values), weights 1 and 3, max 216.
- Check digit (10 - sum % 10) % 10 -> digit 12 is the unique 0..9 with sum + d12 = 10 * q, q one-hot over the multiples of 10 that the sum can reach -> PB equality.
- Objective: satisfaction, output isbn = the 13 digit values as integer expressions.
