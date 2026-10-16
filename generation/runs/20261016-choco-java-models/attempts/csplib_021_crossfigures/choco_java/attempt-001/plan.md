# Plan: crossfigures (9x9 grid, numbered entries equal their clue numbers)

Grid: each entry is a digit string read left-to-right (top-to-bottom); leading digit >= 1.
Cells are digit variables 0..9; cells outside every entry are 0 (black).
Entry value = sum of digit * 10^position (scalar).

Across / down clues -> constraint
- 1 across: 27 across times two -> A1 = 2 * A27
- 4 across: 4 down plus seventy-one -> A4 = D4 + 71
- 7 across: 18 down plus four -> A7 = D18 + 4
- 8 across: 6 down divided by sixteen -> 16 * A8 = D6
- 9 across: 2 down minus eighteen -> A9 = D2 - 18
- 10 across: dozen in six gross -> A10 = 72 (constant)
- 11 across: 5 down minus seventy -> A11 = D5 - 70
- 13 across: 26 down times 23 across -> A13 = D26 * A23 (times)
- 15 across: 6 down minus 350 -> A15 = D6 - 350
- 17 across: 25 across times 23 across -> A17 = A25 * A23 (times)
- 20 across: a square number -> A20 in the set of 4-digit squares
- 23 across: a prime number -> A23 in the set of 2-digit primes
- 24 across: a square number -> A24 in {16,25,36,49,64,81}
- 25 across: 20 across divided by seventeen -> 17 * A25 = A20
- 27 across: 6 down divided by four -> 4 * A27 = D6
- 28 across: four dozen -> A28 = 48 (constant)
- 29 across: seven gross -> A29 = 1008 (constant)
- 30 across: 22 down plus 450 -> A30 = D22 + 450

- 1 down: 1 across plus twenty-seven -> D1 = A1 + 27
- 2 down: five dozen -> D2 = 60 (constant)
- 3 down: 30 across plus 888 -> D3 = A30 + 888
- 4 down: two times 17 across -> D4 = 2 * A17
- 5 down: 29 across divided by twelve -> 12 * D5 = A29
- 6 down: 28 across times 23 across -> D6 = A28 * A23 (times)
- 10 down: 10 across plus four -> D10 = A10 + 4
- 12 down: three times 24 across -> D12 = 3 * A24
- 14 down: 13 across divided by sixteen -> 16 * D14 = A13
- 16 down: 28 down times fifteen -> D16 = 15 * D28
- 17 down: 13 across minus 399 -> D17 = A13 - 399
- 18 down: 29 across divided by eighteen -> 18 * D18 = A29
- 19 down: 22 down minus ninety-four -> D19 = D22 - 94
- 20 down: 20 across minus nine -> D20 = A20 - 9
- 21 down: 25 across minus fifty-two -> D21 = A25 - 52
- 22 down: 20 down times six -> D22 = 6 * D20
- 26 down: five times 24 across -> D26 = 5 * A24
- 28 down: 21 down plus twenty-seven -> D28 = D21 + 27

Objective: none (satisfaction). Output M, 9x9, 0 for cells outside every entry.
