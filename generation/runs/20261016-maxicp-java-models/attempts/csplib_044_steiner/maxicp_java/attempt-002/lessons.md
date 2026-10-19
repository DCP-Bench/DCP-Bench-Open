# csplib_044_steiner, maxicp_java: lessons

attempt-001 (earlier, not retained): accepted on n=3, 7, 9 but timed out on n=13 (json:2, 179 s). Three of four instances checked is 75%, below the 80% bar, so it was not retained.

attempt-002 (retained): the decisions are the elements of each triple, as ints 0..n-1 in increasing order, not the 0/1 matrix. Smallest values come first under firstFailBinary, so the search builds triples from low elements up. Triples are sorted by their smallest element. Symmetry breaking is derived from the relabelling argument: the (n-1)/2 triples through element 0 are fixed to {0,1,2}, {0,3,4}, ... The Boolean matrix is kept as reified views (`isEq` sums) for the pair and column counts.

Run on the four instances: example (n=7), json:1 (n=9), json:2 (n=13, 55 s in the free check against a 180 s limit), json:3 (n=3). No skips.

Tried and dropped before evaluation: a Boolean-matrix decision model (registered `sets` booleans, same pair and column constraints, same symmetry break). A free check on n=13 still timed out at 180 s, so the decision variables were changed to triple elements.
