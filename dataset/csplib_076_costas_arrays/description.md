A Costas array is a pattern of \( n \) marks on an \( n \times n \) grid, one mark per row and one per column, in which the
\( n \cdot (n-1)/2 \) vectors between the marks are all different.
Such patterns are important as they provide a template for generating radar and sonar signals with ideal ambiguity
functions.

A model for Costas Array Problem (CAP) is to define an array of variables \( X_1, \ldots, X_n \) which form a permutation.
For each length \( l \in \{1, \ldots, n-1\} \), we add \( n-l \) more variables \( X_{l1}, \ldots, X_{ln-1} \), whereby each of
these variables is assigned the difference of \( X_i - X_{i+l} \) for \( i \in \{1, \ldots, n-l\} \). These additional variables
form a difference triangle.

Each line of this difference triangle must not contain any value twice. That is, the CAP is simply a collection of
all-different constraints on \( X_1, \ldots, X_n \) and \( X_{l1}, \ldots, X_{ln-l} \) for all \( l \in \{1, \ldots, n-1\} \).

Print the Costas array (costas) as a list of n integers, 1-based indexing.
