Balanced Incomplete Block Design (BIBD) generation is a standard combinatorial problem from design theory, originally
used in the design of statistical experiments but since finding other applications such as cryptography. It is a
special case of Block Design, which also includes Latin Square problems.

A BIBD is defined as an arrangement of \( v \) distinct objects into \( b \) blocks such that each block contains exactly \( k \) distinct objects, each object occurs
in exactly \( r \) different blocks, and every two distinct objects occur together in exactly \( \lambda \) blocks.
Another way of defining a BIBD is in terms of its incidence matrix, which is a \( v \) by \( b \) binary matrix with
exactly \( r \) ones per row, \( k \) ones per column, and with a scalar product of \( \lambda \) between any pair of
distinct rows. A BIBD is therefore specified by its parameters \( (v, b, r, k, \lambda) \). An example of a solution
for \( (7, 7, 3, 3, 1) \) is:

0 1 1 0 0 1 0
1 0 1 0 1 0 0
0 0 1 1 0 0 1
1 1 0 0 0 0 1
0 0 0 0 1 1 1
1 0 0 1 0 1 0
0 1 0 1 1 0 0

Print the incidence matrix of the BIBD (matrix) as a list of lists of integers - 0s and 1s.
