Problem: pick three cards from the dealt cards that form a set (card = [number, fill, color, shape], values 1..3).
- three distinct cards, listed by increasing index -> rel(*this, win[k], IRT_LE, win[k+1]) (strict chain; output is an unordered collection, sorted)
- the card at each chosen index has its feature values -> element(*this, IntArgs(column_f), win[k], feat[3f+k]) for each feature f and card k (column_f = the instance's feature column)
- on each feature the three values are all the same or all different -> extensional(*this, feat_f, TupleSet of the 9 valid triples) (domain consistent per feature, no decomposition into rel)
- branching: win in order with INT_VAR_SIZE_MIN, INT_VAL_MIN; feature values are fixed by element once the index is fixed
- objective: none (satisfaction); output winning_cards = win
