100 bushels of corn distributed among 100 people -> sum of men + women + children == 100 (PB over one-hot integer expressions)
each man received three bushels -> half-bushel units: 6 per man, 4 per woman, 1 per child, total 200 half-bushels (PB over one-hot integers)
each woman two, each child half a bushel -> same weighted sum as above: 6*men + 4*women + children == 200
there are five times as many women as men -> women == 5 * men (PB)
find the number of men, women, and children -> integers men, women, children (one-hot, exactly-one per variable), outputs
objective -> none (satisfaction)
