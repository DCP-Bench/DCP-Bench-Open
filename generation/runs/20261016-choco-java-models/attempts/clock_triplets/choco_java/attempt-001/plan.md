Rearrange the numbers 1 to 12 on the face of a clock -> x[0..11] is a permutation of 1..12: allDifferent(x, "AC")
Each number on the clock appears once; the clock is round -> triplets wrap around (position 11 wraps to 0 and 1)
No triplet of adjacent numbers has a sum higher than 21 -> for each of the 12 triplets (x[i], x[i+1 mod 12], x[i+2 mod 12]): m.sum(triplet, "<=", 21)
Objective: none (satisfaction); output x
