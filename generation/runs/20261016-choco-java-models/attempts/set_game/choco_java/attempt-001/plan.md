The deck consists of 81 unique cards that vary in four features -> cards_data[c] = [number, fill, color, shape] (instance field), c in 0..n-1
Certain combinations of three cards make up a "set" -> winning_cards: 3 distinct card indices, m.allDifferent + m.increasing(w, 1) (strictly increasing, one order per set)
For each one of the four categories of features ... the three cards must display that feature as either all the same, or all different -> per feature f: vals_k = element(cards_data[w_k][f]), m.nValues(vals, nd) with nd in {1,3}
number (feature 0), fill (1), color (2), shape (3) -> one block per feature
satisfaction: find the 0-based indices of the winning set -> output winning_cards, no objective
