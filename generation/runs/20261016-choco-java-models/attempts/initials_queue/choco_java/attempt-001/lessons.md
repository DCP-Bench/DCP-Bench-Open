Pairs are encoded as one IntVar code = 5*first + second, so allDifferent over the codes enforces distinct pairs in one global.
queue[i][a].mul(k).add(b).intVar() builds the code expression directly.
