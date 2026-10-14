Requirements from the description, with the Gecode post for each.

You have a number of bales of hay (n bales, bales = IntVarArray x of size n, domain 0..max weight).
  -> IntVarArray x(*this, n, 0, wmax)

They were weighed in all possible combinations of two; the weights of each combination are the given list, in numerical order, without tracking which pair matched which weight (n(n-1)/2 sums, multiset equality with the list).
  -> sums s_ij = expr(*this, x[i] + x[j]) for i < j; the multiset of sums equals the list: count(*this, sums, IntSetArgs(multiplicity of each distinct weight), IntArgs(distinct weights), IPL_DOM) (gcc with fixed cardinalities, every sum forced to a listed value). Rows of the gcc map: "value v_j occurs c_j times".

Symmetry (output convention): bales listed in increasing order, as the reference solves with bales sorted. Not a constraint of the description, but every solution set is closed under permutation of x, so sorting loses no answer up to order.
  -> rel(*this, x[i], IRT_LQ, x[i+1]) for consecutive i (lexicographic chain via rel on each pair)

Implied (redundant) constraint: each bale appears in n-1 pairs, so (n-1) * sum(x) = sum of all weights.
  -> linear(*this, IntArgs(n-1 copies of 1, -1 ...)) written as rel(*this, (n-1) * sum(x) == S) with S the total of the list; this is a derivation from the description.

Branching: the bales in order from the smallest, smallest value first, since the sorted order and the two-smallest-sums fix x0 quickly.
  -> branch(*this, x, INT_VAR_NONE(), INT_VAL_MIN())

Objective: none (satisfaction). Output: bales = x.
  -> output("bales", x)
