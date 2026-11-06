The ternary Steiner problem of order \( n \) consists of finding a set of \( n \cdot (n-1)/6 \) triples of distinct
integer elements in \(\{1, \ldots, n\}\) such that any two triples have at most one common element. It is a hypergraph
problem coming from combinatorial mathematics where \( n \) modulo 6 has to be equal to 1 or 3.
One possible solution for \( n = 7 \) is \(\{\{1, 2, 3\}, \{1, 4, 5\}, \{1, 6, 7\}, \{2, 4, 6\},
\{2, 5, 7\}, \{3, 4, 7\}, \{3, 5, 6\}\}\). The solution contains \( 7 \cdot (7-1)/6 = 7 \) triples.
This is a particular case of the more general Steiner system.

Print the set of triples (sets) as a boolean matrix where each row represents a triple and each column represents an
element. The value of the matrix at position [i, j] is true if element j is part of triple i, and false otherwise.
