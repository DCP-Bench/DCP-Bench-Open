# Plan: csplib_015 Schur's lemma

- each ball i in 1..n is in exactly one of the c boxes -> one-hot Bools M[i][j], sum over j == 1
- for any triple of balls x + y = z (x <= y, z <= n) and each box j, not all three in box j -> clause ~M[x][j] | ~M[y][j] | ~M[z][j] (duplicates removed when x == y)
- output balls[i] = box number of ball i -> sum((j+1) * M[i][j]) over j
- objective -> satisfaction (no objective)
