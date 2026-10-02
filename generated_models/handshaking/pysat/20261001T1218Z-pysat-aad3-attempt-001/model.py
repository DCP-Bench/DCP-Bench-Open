# Handshaking: Hilary and Jocelyn are married and invite a number of couples. People shake
# hands with each other, but nobody with themselves or their spouse. Everybody except Hilary
# has shaken a different number of hands. How many hands has Hilary shaken?
from pysat.card import CardEnc, EncType
from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def build(instance):
    couples = instance["num_couples"]  # invited couples, not counting Hilary and Jocelyn
    n = 2 + 2 * couples                # people: 0 = Hilary, 1 = Jocelyn, then the couples (2, 3), (4, 5), ...

    def spouse(i):
        return i ^ 1  # the people 2c and 2c + 1 are married

    pool = IDPool()
    # shake[i, j] (i < j) is true when persons i and j shake hands. The handshake is symmetric,
    # so one variable serves both directions; nobody shakes with themselves or their spouse.
    shake = {(i, j): pool.id(("shake", i, j))
             for i in range(n) for j in range(i + 1, n) if j != spouse(i)}
    hands = [[shake[min(i, j), max(i, j)] for j in range(n) if j != i and j != spouse(i)]
             for i in range(n)]

    # deg[i] = number of hands person i has shaken; at most n - 2 (everybody but self and spouse)
    deg = [Integer(f"deg{i}", 0, n - 2, encoding="coupled", vpool=pool) for i in range(n)]
    engine = IntegerEngine(vars=deg, vpool=pool)

    # everybody except Hilary has shaken a different number of hands
    engine.add_alldifferent(deg[1:])

    # Symmetry breaking. The couples can be renamed among themselves, and the two spouses of a
    # couple can be swapped, without changing Hilary's count, so each couple lists its spouse
    # with more handshakes first, and the couples are ordered by that first spouse's count (all
    # counts are different, so the order is strict). The declared output (Hilary's count) is
    # unchanged: every solution can be renamed into this form.
    for c in range(1, couples + 1):
        engine.add_linear(deg[2 * c] - deg[2 * c + 1] >= 1)
        if c < couples:
            engine.add_linear(deg[2 * c] - deg[2 * c + 2] >= 1)

    cnf = engine.clausify()

    # deg[i] counts the handshakes of person i: for every value v, "deg[i] = v" forces exactly v of
    # the handshake variables of i to be true. Each clause of the cardinality encoding carries the
    # guard "deg[i] != v", so the encoding binds only when deg[i] = v (its auxiliary variables are
    # fresh and free otherwise).
    for i in range(n):
        for v in range(n - 1):
            guard = -deg[i].equals(v)
            for clause in CardEnc.equals(lits=hands[i], bound=v, vpool=pool,
                                         encoding=EncType.seqcounter).clauses:
                cnf.append([guard] + clause)

    # Redundant: the n - 1 people other than Hilary have n - 1 different counts among the
    # n - 1 values 0..n-2, so every value occurs; this is stated to help the solver.
    for v in range(n - 1):
        cnf.append([deg[i].equals(v) for i in range(1, n)])

    return cnf, {"hil": deg[0]}
