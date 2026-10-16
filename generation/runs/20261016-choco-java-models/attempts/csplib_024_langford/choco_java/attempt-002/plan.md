Langford pairing, k pairs, sequence of 2k positions (0-based)
"two sets of the numbers from 1 to k" -> one pair of positions per number i, pair positions x_i and y_i
"arrange the 2k numbers into a single sequence" -> all 2k pair positions different, allDifferent over {x_i, y_i}
"the two i's appear i numbers apart" -> y_i = x_i + i + 1 (explicit variable tied by arithm, not an offset view)
"print the solution sequence as a list of 2k integers" -> sol[p] = i iff p in {x_i, y_i}: element(i, sol, x_i) and element(i, sol, y_i)
objective -> satisfaction, no objective
