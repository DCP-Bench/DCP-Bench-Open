Three people X, Y, Z seated around a table; seats 0, 1, 2; 1 is right of 0, 2 right of 1 (and 0 right of 2) -> seat p's right neighbour is (p+1) mod 3; values 0..2 -> one-hot per name, all different (x, y, z a permutation).
Nationalities American, English, French are a permutation of seats 0..2 -> one-hot, all different.
Y passed three hearts to the American -> the American sits on Y's right: american = (y+1) mod 3 -> Iff(y == v, american == (v+1) mod 3) for each v.
X passed the queen of spades and two diamonds to the person who passed their cards to the Frenchwoman -> X passed to Q at (x+1) mod 3; Q passed to the Frenchwoman at (x+2) mod 3 -> french = (x+2) mod 3 -> Iff(x == v, french == (v+2) mod 3) for each v.
Objective: none (satisfaction); outputs x, y, z, american, english, french = seat values.
