A partition of numbers 1..N into two sets A and B -> one Bool a[i][j] per (number i, A-slot j) and b[i][j] per (number i, B-slot j), each number in exactly one slot (exactly one of its a/b Bools); the slots hold the output lists, one-hot per slot
A and B have the same cardinality -> each A-slot and each B-slot holds exactly one number, so |A| = |B| = N/2
Sum of numbers in A = sum of numbers in B -> sum_i i*(A-membership) == sum_i i*(B-membership), as one PB over the slot Bools
Sum of squares in A = sum of squares in B -> sum_i i^2*(A-membership) == sum_i i^2*(B-membership), one PB with weights i^2
Slots are sorted increasing (A_j < A_j+1, B_j < B_j+1) -> integer slot values A_j = sum_i i*a[i][j], pairwise strict order (symmetry breaking on the output only)
Objective -> satisfaction (none)
