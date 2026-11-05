Find a set \( S \) of `num_words` strings (words) of length `n` over the alphabet \( W = \{ A,C,G,T \} \) with the following properties:

- Each word in \( S \) has 4 symbols from \{ C,G \};
- Each pair of distinct words in \( S \) differ in at least 4 positions; and
- Each pair of words \( x \) and \( y \) in \( S \) (where \( x \) and \( y \) may be identical) are such that \( x^R \) and \( y^C \) differ in at least 4 positions. For example, when n=8, \( ( x_1,\ldots,x_8 )^R = ( x_8,\ldots,x_1 ) \) is the reverse of \( ( x_1,\ldots,x_8 ) \) and \( ( y_1,\ldots,y_8 )^C \) is the Watson-Crick complement of \( ( y_1,\ldots,y_8 ) \), i.e. the word where each \( A \) is replaced by a \( T \) and vice versa and each \( C \) is replaced by a \( G \) and vice versa.

Print the set of words (words) as a list of lists of integers, where each integer represents a letter in the word: 1 for A, 2 for C, 3 for G, and 4 for T.
