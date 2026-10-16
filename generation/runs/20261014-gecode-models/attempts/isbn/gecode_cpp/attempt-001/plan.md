# Plan: isbn (ISBN-13 check digit completion)

Problem: fill the unknown digits (-1) of a 13-digit ISBN so that it is valid and starts with 978 or 979.

- each digit is one of 0..9 -> IntVarArray isbn(*this, 13, 0, 9)
- a given digit (not -1) stays as given -> rel(isbn[i] == init[i]) for each fixed position
- starts with 978 or 979: first digit 9, second digit 7 -> rel(isbn[0] == 9), rel(isbn[1] == 7)
- starts with 978 or 979: third digit 8 or 9 -> rel(isbn[2] >= 8)
- weights alternate 1 and 3 from the first digit, check digit is (10 - sum % 10) % 10, so the weighted sum of all 13 digits is a multiple of 10 -> linear(weights 1,3,..,1 over isbn, minus 10*K, IRT_EQ 0, IPL_DOM) with K in 0..22 (max weighted sum is 9*25 = 225)
- branching: isbn in order, smallest value first; K is fixed by propagation once isbn is assigned
- objective: none (satisfaction)
