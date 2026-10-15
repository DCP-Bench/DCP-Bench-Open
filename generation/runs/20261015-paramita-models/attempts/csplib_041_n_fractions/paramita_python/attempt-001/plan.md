Find distinct non-zero digits A..I -> one-hot digit Bools d[X][v], v in 1..9, exactly one value per digit: sum_v d[X][v] == 1
Distinct digits (nine digits, values 1..9) -> each value used by exactly one digit: sum_X d[X][v] == 1 for each v
BC = 10B+C, EF = 10E+F, HI = 10H+I -> binary bits (7 each) p, q, r with sum_i 2^i bit == 10*tens + units (one-hot digits, linear)
A/BC + D/EF + G/HI = 1 -> multiply by BC*EF*HI: A*EF*HI + D*BC*HI + G*BC*EF == BC*EF*HI
Products of bits: QR[i][j] = q_i & r_j, PR, PQ as Bools; triple Bools digit & two bits, PB sums with weights 2^(i+j) * value
Print the values (A..I) -> integer outputs A..I, each sum_v v * d[X][v]
Objective: satisfaction (no objective)
