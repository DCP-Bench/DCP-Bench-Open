# Word design for DNA computing: find num_words strings of length n over the alphabet
# A, C, G, T (written 1, 2, 3, 4) such that every word has exactly 4 symbols from {C, G},
# any two distinct words differ in at least 4 positions, and for any two words x and y
# (possibly the same word) the reverse of x and the Watson-Crick complement of y differ
# in at least 4 positions.
from itertools import combinations

from pysat.card import CardEnc, EncType
from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine

A, C, G, T = 1, 2, 3, 4  # letters, as the reference numbers them (problem constants)
CG_PER_WORD = 4          # number of C or G symbols in each word (problem constant)
MIN_DISTANCE = 4         # required number of differing positions (problem constant)


def build(instance):
    n = instance["n"]                # length of each word
    num_words = instance["num_words"]  # number of words to find

    pool = IDPool()
    # words[i][j] = the j-th letter of the i-th word. The direct encoding gives the
    # literal words[i][j].equals(a) for "this letter is a"; exactly one is true.
    words = [[Integer(f"word{i}_{j}", A, T, vpool=pool) for j in range(n)]
             for i in range(num_words)]
    engine = IntegerEngine(vars=[letter for word in words for letter in word], vpool=pool)
    cnf = engine.clausify()
    is_letter = [[{a: words[i][j].equals(a) for a in range(A, T + 1)} for j in range(n)]
                 for i in range(num_words)]

    def at_least_differ(first, second, key):
        """first[j][a] and second[j][a] are the literals for "position j holds letter a".
        Require at least MIN_DISTANCE positions where the two words differ.
        differ[j] is only forced to imply a real difference, which is all the count needs."""
        differ = []
        for j in range(n):
            flag = pool.id((key, j))
            for a in range(A, T + 1):
                cnf.append([-flag, -first[j][a], -second[j][a]])  # same letter => no difference
            differ.append(flag)
        cnf.extend(CardEnc.atleast(lits=differ, bound=MIN_DISTANCE, vpool=pool,
                                   encoding=EncType.seqcounter).clauses)

    # each word has exactly 4 symbols from {C, G}: a position holds C or G in at most one
    # of the two literals, so counting both literals over the word counts those positions
    for i in range(num_words):
        lits = [is_letter[i][j][a] for j in range(n) for a in (C, G)]
        cnf.extend(CardEnc.equals(lits=lits, bound=CG_PER_WORD, vpool=pool,
                                  encoding=EncType.seqcounter).clauses)

    # any two distinct words differ in at least 4 positions
    for x, y in combinations(range(num_words), 2):
        at_least_differ(is_letter[x], is_letter[y], ("differ", x, y))

    # for any words x and y (also x = y), reverse(x) and the Watson-Crick complement of y
    # differ in at least 4 positions. The complement of letter a is 5 - a (A<->T, C<->G),
    # so position j of the complement of y holds letter a exactly when y[j] holds 5 - a.
    for x in range(num_words):
        reverse_x = [is_letter[x][n - 1 - j] for j in range(n)]
        for y in range(num_words):
            complement_y = [{a: is_letter[y][j][T + A - a] for a in range(A, T + 1)}
                            for j in range(n)]
            at_least_differ(reverse_x, complement_y, ("rc", x, y))

    return cnf, {"words": words}
