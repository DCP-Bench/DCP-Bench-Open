The number uses each of the digits 0 to 9 exactly once -> distinct(*this, digit, IPL_DOM) over 10 digits in 0..9 (a permutation)
The number is 10 digits long, so its leading digit is not 0 -> rel(*this, digit[0] != 0)
The number formed by the first 1 digit is divisible by 1 -> trivially true, no constraint; prefix[0] == digit[0] links the chain
The number formed by the first n digits is the first n-1 digits shifted left plus digit n (n = 2..9) -> rel(prefix[n-1] == 10*prefix[n-2] + digit[n-1]) (linear, bounds, exact on values below 10^9)
The number formed by the first n digits is divisible by n (n = 2..9) -> rel(prefix[n-1] == n*quot[n-1]) with quot an auxiliary quotient; linear, no mod decomposition
The number formed by the first 10 digits is divisible by 10 -> derived: whole = 10*prefix9 + digit[9], so divisibility by 10 holds iff digit[9] == 0 -> rel(*this, digit[9] == 0)
Branching: digits left to right (INT_VAR_NONE, INT_VAL_MIN) so each divisibility check prunes at its own level; then prefix and quot (fixed by propagation, branched for safety)
Objective: none (satisfaction); output "number" via output_digits (10 digits, base 10, exceeds the IntVar range)
