the blocks contain every letter but Q and Z (24 letters) -> one-hot Bool y[l][b] for each letter l in the alphabet and block b in 0..num_blocks-1, exactly one block per letter: sum(y[l]) == 1
each of the blocks has a single letter on each of its sides -> per block b: sum(y[l][b] for l) == num_sides
By arranging the blocks in various ways, you can spell all of the words in a given list -> for each word and each block b: sum(y[l][b] for l in the word's letters) <= 1 (the word's letters sit on distinct blocks)
Print the solution as a list of num_letters numbers representing at which block each letter is placed (dice) -> dice[l] = sum(b * y[l][b] for b), outputs "dice" in alphabet order
Objective -> satisfaction, no objective
