# plan: five_brigands

Five brigands Alfonso, Benito, Carlos, Diego, Esteban captured altogether exactly 200 doubloons
-> A+B+C+D+E = 200, m.sum(x, "=", 200)
if Alfonso had 12 times as much, Benito 3 times, Carlos the same, Diego half, Esteban one-third, the total is still 200
-> 12A+3B+C+D/2+E/3 = 200, scaled by 6 to 72A+18B+6C+3D+2E = 1200, m.scalar(x, coeffs, "=", 1200)
no brigand had less than one doubloon
-> each of A..E in 1..200 (domain lower bound 1)
objective: none (satisfaction); outputs A, B, C, D, E
