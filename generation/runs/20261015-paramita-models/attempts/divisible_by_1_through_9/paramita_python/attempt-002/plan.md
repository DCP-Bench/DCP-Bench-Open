# Plan: divisible_by_1_through_9

Digits: one-hot y[p][v] (position p = 1..10 from the left, digit v = 0..9).

- "Find a 10 digit number" -> every position holds exactly one digit: sum_v y[p][v] == 1; leading digit nonzero: ~y[1][0].
- "uses each of the digits 0 to 9 exactly once" -> each digit sits in exactly one position: sum_p y[p][v] == 1.
- "the number formed by the first n digits of the number is divisible by n" for n = 2..10 (n = 1 is trivially true) -> per n:
  prefix value = sum_{p<=n} 10^(n-p) d_p; replace each weight by 10^(n-p) mod n (same residue, small weights);
  sum_{p<=n} r_p d_p == n * t, with t one-hot over 0..M_n.
- "Print the number (number)" -> number = sum_p 10^(10-p) d_p (int expression, read exactly by the runner).
- Objective -> satisfaction (none).
- Weights stay below 2^31 for the output; no constraint is posed on the large number itself, so no 32-bit wrap in constraints.
