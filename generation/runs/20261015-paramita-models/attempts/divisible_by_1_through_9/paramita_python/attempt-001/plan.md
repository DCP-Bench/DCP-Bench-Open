# Plan: divisible_by_1_through_9

Digits: one-hot y[p][v] (position p = 1..10, digit v = 0..9).

- "a 10 digit number" -> each position exactly one digit (sum_v y[p][v] == 1); leading digit nonzero (~y[1][0]).
- "uses each of the digits 0 to 9 exactly once" -> each digit at exactly one position (sum_p y[p][v] == 1).
- "the number formed by the first n digits is divisible by n" for n = 1..10 -> per k:
  prefix P_k = sum_{p<=k} 10^(k-p) d_p; replace 10^(k-p) by c = 10^(k-p) mod k (same value mod k), so
  sum_{p<=k} c_p d_p = k * t, with t one-hot over 0..M_k (small weights).
- Number output -> number = sum_p 10^(10-p) d_p (int expression). Note: value can exceed 2^31.
- Objective -> satisfaction (none).
