Each cow goes to exactly one son -> one-hot son per cow, x[i][s] Bools, sum over s == 1 per cow
The farmer distributes his cows to them according to a given distribution -> sum over cows x[i][s] == cows_per_son[s] per son (instance field)
Each cow gives a quantity of milk equal to its number -> milk term i * x[i][s] with cow i numbered 1..num_cows
The total quantity of milk should be the same for each son -> per son s > 0: sum_i i * x[i][s] == sum_i i * x[i][0] (PB equality)
Print cow_assignments: the son of cow i (0-based son index) -> sum over s of s * x[i][s] per cow, as integer expressions
Objective: none (satisfaction)
