# Circling the squares (Dudeney): put a different number in each of the ten squares of a circle
# so that the sum of the squares of any two adjacent numbers equals the sum of the squares of
# the two numbers diametrically opposite to them. Four numbers are given, and no number needs
# more than two figures.
from pysat.card import CardEnc, EncType
from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def build(instance):
    names = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "K"]  # the ten squares, around the circle
    # The four numbers given in the problem statement (the problem has no instance data).
    given = {"A": 16, "B": 2, "F": 8, "G": 14}
    largest = 99  # no number needs more than two figures

    pool = IDPool()
    # x[name] = the number placed in that square
    x = {name: Integer(name, 1, largest, vpool=pool) for name in names}
    engine = IntegerEngine(vars=list(x.values()), vpool=pool)

    # all ten numbers are different
    engine.add_alldifferent(list(x.values()))

    # the numbers that are given
    for name, value in given.items():
        engine.add_linear(x[name] == value)

    cnf = engine.clausify()

    # same_sum_of_squares(x1, x2, y1, y2): x1^2 + x2^2 == y1^2 + y2^2.
    # PySAT cannot multiply two variables, so squares are tabulated. The literal sums[s] stands
    # for "the common sum of squares is s": every pair of values of (x1, x2) and of (y1, y2)
    # forces the literal of its own sum, and at most one sum literal may hold, so both pairs
    # have to give the same sum.
    def same_sum_of_squares(x1, x2, y1, y2, tag):
        sums = {}
        for first, second in ((x1, x2), (y1, y2)):
            for v1 in range(1, largest + 1):
                for v2 in range(1, largest + 1):
                    s = v1 * v1 + v2 * v2
                    if s not in sums:
                        sums[s] = pool.id(("sum", tag, s))
                    cnf.append([-first.equals(v1), -second.equals(v2), sums[s]])
        cnf.extend(CardEnc.atmost(lits=list(sums.values()), bound=1, vpool=pool,
                                  encoding=EncType.seqcounter).clauses)

    # each pair of adjacent squares has the same sum of squares as the pair opposite to it
    A, B, C, D, E, F, G, H, I, K = (x[name] for name in names)
    same_sum_of_squares(A, B, F, G, "AB")
    same_sum_of_squares(B, C, G, H, "BC")
    same_sum_of_squares(C, D, H, I, "CD")
    same_sum_of_squares(D, E, I, K, "DE")
    same_sum_of_squares(E, F, K, A, "EF")

    return cnf, {name: x[name] for name in names}
