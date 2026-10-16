Problem: find distinct non-zero digits A..I with A/BC + D/EF + G/HI = 1, where BC, EF, HI are two-digit numbers.
Distinct non-zero digits -> allDifferent(A,B,C,D,E,F,G,H,I) over 1..9 (nine distinct values from 1..9)
BC = 10B + C -> x = 10*B + C, with x in 10..99
EF = 10E + F -> y = 10*E + F, with y in 10..99
HI = 10H + I -> z = 10*H + I, with z in 10..99
A/BC + D/EF + G/HI = 1 with no fractions -> multiply by xyz: A*y*z + D*x*z + G*x*y = x*y*z
Objective: satisfaction (none)
