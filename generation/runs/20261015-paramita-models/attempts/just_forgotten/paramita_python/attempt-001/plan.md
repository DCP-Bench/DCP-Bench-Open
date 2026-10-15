Just forgotten: the account number is a permutation of the digits 0 to n-1, with n the length of each set.

- The account number has all the digits from 0 to n-1 in some order. -> one-hot xv[i][v] per position i and digit v; each position holds one digit: sum_v xv[i][v] == 1; each digit appears once: sum_i xv[i][v] == 1
- In each set, exactly k digits are in their correct position (k = num_correct_digits). -> for each set s: sum_i xv[i][s[i]] == k (one-hot literal of the set's digit at position i)
- Output x: the account number, x_i = sum_v v * xv[i][v] (integer expression).
- Objective: none (satisfaction).
