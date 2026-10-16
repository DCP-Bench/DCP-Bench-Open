Variables a_1..a_l, b_1..b_l, each in {-1,+1}, l odd from the instance -> IntVarArray with IntSet({-1,1}) domains
Hadamard Legendre pairs: PAF(A,s) + PAF(B,s) = -2 for s = 1..m, m = (l-1)/2 -> per s, products a_i * a_{(i+s) mod l} and b_i * b_{(i+s) mod l} (i = 0..l-1) as {-1,1} IntVars via mult(IPL_DOM); linear(sum of the 2l products == -2) (linear over products, bounds)
sum of a_i = 1 -> linear(*this, a, IRT_EQ, 1)
sum of b_i = 1 -> linear(*this, b, IRT_EQ, 1)
branching -> branch a then b with INT_VAR_SIZE_MIN / INT_VAL_MIN (domains are all size 2, so first-fail ties; restarts only if evaluation times out)
objective -> none (satisfaction); outputs a and b as IntVarArray
