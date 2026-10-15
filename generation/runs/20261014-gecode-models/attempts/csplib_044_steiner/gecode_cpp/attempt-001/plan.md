the ternary Steiner problem of order n: a set of n(n-1)/6 triples of distinct elements of {1..n}
  -> one Boolean row per triple (T = n(n-1)/6 rows, n columns; x[t][j] = element j in triple t), 0-based internally, printed as rows of the boolean matrix
each triple consists of exactly three distinct elements
  -> linear(*this, row_t, IRT_EQ, 3) over the Booleans of each row
any two triples have at most one common element
  -> per pair of triples: expr(*this, x[t1][j] && x[t2][j]) over j, then linear(*this, both, IRT_LQ, 1) (no decomposition: a reified sum is the only encoding of this clause)
redundant, implied by counting (3T = n(n-1)/2 pairs, each pair in at most one triple): every pair of elements lies in exactly one triple
  -> per pair of elements: expr(*this, x[t][a] && x[t][b]) over t, then linear(*this, cover, IRT_EQ, 1)
redundant, implied by counting: every element lies in (n-1)/2 triples
  -> linear(*this, column_j, IRT_EQ, (n-1)/2)
the triples form a set, so their order is free
  -> lexicographic order on consecutive rows: rel(*this, row_t, IRT_LQ, row_{t+1}); two equal rows are impossible, so the order is strict in effect
branching: row by row, Booleans in order, value 1 first (fills the first triple, the rest follows from the sums and the pair cover)
  -> branch(*this, x, BOOL_VAR_NONE(), BOOL_VAL_MAX())
objective: none (satisfaction)
