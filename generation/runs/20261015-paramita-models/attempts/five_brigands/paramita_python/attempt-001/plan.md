# five_brigands plan (attempt-001)

- Five brigands had captured altogether exactly 200 doubloons -> A + B + C + D + E == 200, each an integer expression (unary encoding, 1 + sum of order Bools).
- If Alfonso had twelve times as much, Benito three times, Carlos the same, Diego half, Esteban one-third, the total would still be 200 -> 12A + 3B + C + D/2 + E/3 == 200, multiplied by 6 to stay in integers: 72A + 18B + 6C + 3D + 2E == 1200.
- No brigand had less than one doubloon -> base 1 of the unary encoding (every value >= 1).
- Upper bound: at most the total 200 (from the first constraint, each value <= 200).
- Objective: none, the output is any solution (satisfaction). Outputs A, B, C, D, E as integer expressions.
