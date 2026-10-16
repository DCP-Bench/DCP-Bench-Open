Place a different number in each of the ten squares -> allDifferent over the ten values (AC)
Numbers are whole numbers and no number needs more than two figures -> domain 1..99 (positive integers; the description allows no fractions)
The sum of the squares of any two adjacent numbers equals the sum of the squares of the two numbers diametrically opposite -> for each of the 5 adjacent pairs (p_i, p_i+1) and its opposite pair (p_i+5, p_i+6 mod 10): sq_i + sq_i+1 - sq_i+5 - sq_i+6 = 0 (scalar with squares from m.square)
The four given numbers A=16, B=2, F=8, G=14 -> fixed values
Objective: none (satisfaction); output A..I and K
