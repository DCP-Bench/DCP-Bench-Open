from pycsp3 import *

# Find num_words words of length n over the alphabet A, C, G, T (coded 1, 2, 3, 4).
# Each word has four symbols from C and G, distinct words differ in at least four
# positions, and for every pair of words x and y (possibly identical) the reverse of x
# and the Watson-Crick complement of y differ in at least four positions.

n = data.n
num_words = data.num_words

# words[s][k] is the letter at position k of word s; 1 A, 2 C, 3 G, 4 T
words = VarArray(size=[num_words, n], dom=range(1, 5))

# complements[s][k] is the Watson-Crick complement of the letter at position k of word s
# (A and T swap, C and G swap, so the complement of letter v is 5 - v)
complements = VarArray(size=[num_words, n], dom=range(1, 5))

# strong[s][k] is 1 when position k of word s is C or G, and 0 when it is A or T
strong = VarArray(size=[num_words, n], dom={0, 1})

# the reverse of word s is the same letters read from the last position to the first
reverses = [[words[s][n - 1 - k] for k in range(n)] for s in range(num_words)]

satisfy(
    # a letter is C or G exactly when its indicator is 1
    [Table(scope=[words[s][k], strong[s][k]], supports=[(1, 0), (2, 1), (3, 1), (4, 0)])
     for s in range(num_words) for k in range(n)],

    # each word has exactly four symbols from C and G
    [Sum(strong[s]) == 4 for s in range(num_words)],

    # the complement letters are the Watson-Crick complement of each word
    [complements[s][k] == 5 - words[s][k] for s in range(num_words) for k in range(n)],

    # distinct words differ in at least four positions
    [Hamming(words[s], words[t]) >= 4 for s in range(num_words) for t in range(s + 1, num_words)],

    # the reverse of x and the complement of y differ in at least four positions, for every pair x, y
    [Hamming(reverses[s], complements[t]) >= 4 for s in range(num_words) for t in range(num_words)],
)
