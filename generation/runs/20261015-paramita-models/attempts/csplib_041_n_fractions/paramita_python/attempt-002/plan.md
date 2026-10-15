Find distinct non-zero digits (A, B, ..., I) -> nine digit variables, one-hot over 1..9 each, exactly one value per variable, and each value 1..9 used once (all different: a permutation of 1..9)
Two-digit numbers BC, EF, HI formed by the digits -> X = 10*B + C, Y = 10*E + F, Z = 10*H + I as one-hot over the two-digit values, linked to the digits by Iff(X_xy, B_x & C_y)
A/BC + D/EF + G/HI = 1 -> cross-multiplied A*Y*Z + D*X*Z + G*X*Y = X*Y*Z, encoded as a table over the digit tuples (B, C, E, F, A, D, G): the tuple forces (H, I) by Z = G*X*Y / (X*Y - A*Y - D*X), or is forbidden when no two-digit Z satisfies it
Print the values (A, B, C, D, E, F, G, H, I) -> outputs are the digit expressions sum_v v * one-hot
Objective: none, satisfaction
