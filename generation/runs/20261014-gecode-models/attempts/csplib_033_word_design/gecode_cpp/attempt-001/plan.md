Problem: find num_words words of length n over {A,C,G,T} (1,2,3,4), with the constraints below.
Each word has 4 symbols from {C,G} -> count(*this, word, IntSet(2,3), IRT_EQ, 4) per word (domain-consistent count with a set).
Each pair of distinct words differs in at least 4 positions -> per pair, BoolVar e_k = (w_i[k] == w_j[k]) for each k, then linear(*this, e, IRT_LQ, n-4). No Gecode global measures Hamming distance; the reified sum is the only fit (the same encoding the map gives for "how many are true").
For every ordered pair x,y (x = y allowed): reverse(x) and complement(y) differ in at least 4 positions -> per pair and position k, BoolVar b_k = (x[n-1-k] + y[k] == 5) since the Watson-Crick complement of v is 5-v (A=1<->T=4, C=2<->G=3); then linear(*this, b, IRT_LQ, n-4). Same reified-sum reason as above; pairs over all ordered (w,w2) including the diagonal.
Set symmetry: the words form a set, so rows are ordered lexicographically -> rel(*this, rowA, IRT_LQ, rowB) on consecutive words (distinct words make LQ equivalent to LE).
Branching: letters in row-major order (word by word), INT_VAR_SIZE_MIN, INT_VAL_MIN.
Objective: none (satisfaction). Outputs: words as std::vector<IntVarArgs>, one list per word.
