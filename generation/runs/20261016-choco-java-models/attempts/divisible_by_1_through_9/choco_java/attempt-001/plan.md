# plan: divisible_by_1_through_9

Find a 10 digit number that uses each of the digits 0 to 9 exactly once
-> d[0..9] in 0..9, m.allDifferent(d, "AC")
10 digit number, so the first digit is not 0
-> d[0].ne(0).post()
the number formed by the first n digits is divisible by n (n = 1..10)
-> for each n: remainder chain r_1 = d[0] mod n, r_k = (10*r_{k-1} + d[k-1]) mod n for k = 2..n (m.mod with small bounded IntVars), then r_n = 0
objective: none (satisfaction); output number = digits d as 10-digit number -> out.putDigits("number", d, 10)
