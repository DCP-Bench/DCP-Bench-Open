Complete the puzzle: 8 entries (1 across len5, 2 down len5, 3 down len5, 4 across len4, 5 down len4, 6 down len3, 7 across len3, 8 across len5), each filled by one word -> w[e] in 0..14 for each entry, allDifferent(w) (the 8 chosen words are different)
Word list: 15 words sorted by length then alphabetically: HOSES, LASER, SAILS, SHEET, STEER (5); HEEL, HIKE, KEEL, KNOT, LINE (4); AFT, ALE, EEL, LEE, TIE (3)
Each entry's letters are the word's letters -> table (w[e], cells of e) with one tuple per word of the entry's length
Crossing squares share one letter -> the same cell variable is used by both entries through it
Output E: the chosen word index for each entry, in clue-number order -> out.put("E", w)
Objective: none (satisfaction)
