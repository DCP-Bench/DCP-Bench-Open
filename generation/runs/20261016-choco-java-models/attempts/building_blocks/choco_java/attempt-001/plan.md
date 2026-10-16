building_blocks plan
each block has a single letter on each of its sides, num_sides sides per block -> dice[letter] = block index in 0..num_blocks-1, each block holds exactly num_sides letters -> globalCardinality(dice, 0..num_blocks-1, occ = num_sides each, closed)
the blocks contain every letter but Q and Z -> one die variable per letter of the alphabet string (num_letters letters)
by arranging the blocks you can spell all words in the list -> for each word: the blocks of its letters are all different (a word uses each block at most once) -> allDifferent over dice[letter] for the letters of the word
objective: none (satisfaction)
