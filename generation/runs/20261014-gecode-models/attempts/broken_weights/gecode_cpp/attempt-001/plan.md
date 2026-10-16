A merchant's measuring weight broke into n pieces; each piece weighs a whole number of pounds
  -> w[i] in 1..m (IntVarArray with domain 1..m, m and n from the instance)
the pieces weigh m pounds in total (the total weight)
  -> linear(*this, w, IRT_EQ, m)
the pieces can be used to weigh every integer from 1 to m
  -> for each k in 1..m, a weighing of k on the object pan: pieces on the object pan (left) and on the weights pan (right), each piece on at most one pan; sum(left pieces) - sum(right pieces) == k (linear over mult products w[i]*left, w[i]*right)
  -> the balance: k + sum(right) == sum(left), placed as one linear over the products (bounds via IPL_BND default)
the pieces are sorted by weight, strictly increasing; this is symmetry breaking and also gives all-different (no valid answer repeats a weight)
  -> rel(*this, w[i], IRT_LE, w[i+1])
branching: pieces first (INT_VAR_SIZE_MIN, INT_VAL_MIN), then the pan placements of every weighing (BOOL_VAR_NONE, BOOL_VAL_MIN)
objective: none (satisfaction); output weights
