Cryptarithm: BAIJJAJIIAHFCFEBBJEA + DHFGABCDIDBIFFAGFEJE = GJEGACDDHFAFJBFIHEEF (20-digit addends, letters A..J)
letters A..J are distinct digits 0..9 -> distinct(*this, letters, IPL_DOM)
leading letters B (first addend), D (second addend), G (sum) are not zero -> domain 1..9 via rel(letter, IRT_GQ, 1)
20 columns, carries from the right: column i: top[i] + bottom[i] + carry_in = sum[i] + 10*carry_out -> linear(IntArgs{1,1,1,-1,-10}, IntVarArgs, IRT_EQ, 0, IPL_DOM) (small coefficients, avoids 10^19 overflow of a single linear sum)
no carry into the rightmost column and none out of the leftmost (sum has 20 digits) -> carry[0] = 0, carry[20] = 0; carries are 0..1 -> rel(carry, IRT_LQ, 1)
branching: letters first (INT_VAR_SIZE_MIN, INT_VAL_MIN), then carries (determined by the letters)
objective: none (satisfaction); outputs A..J are the letter variables
