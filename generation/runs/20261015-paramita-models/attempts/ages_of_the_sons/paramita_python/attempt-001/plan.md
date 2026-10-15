The product of their ages is 36. -> candidate table: every sorted triple (A1 >= A2 >= A3) of positive divisors of 36 with product 36; one-hot selector t over candidates (one true) for the real ages.
I need more information. -> no constraint beyond the table (the product alone leaves several candidates).
The sum of their ages equals the number of windows (unknown). I need more information. -> second one-hot selector v over candidates (one true), v differs from t, v has the same sum as t (sum groups from the table); t lies in a sum group with two or more candidates.
The oldest son has blue eyes. I got it. -> the oldest son is unique (A1 > A2), so candidates with A1 = A2 are false; for each unique-oldest candidate j, if t's sum equals j's sum then t is j.
Print the ages A1, A2, A3 starting from the oldest. -> outputs as integer expressions sum(age * selector).
Objective: none, satisfaction.
