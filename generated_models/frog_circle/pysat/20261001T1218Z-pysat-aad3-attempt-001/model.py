# Frog circle: arrange the cards 1..n in a circle so that a frog that starts on card 1 and,
# from card k, jumps k places clockwise visits every card.
from pysat.card import CardEnc, EncType
from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def build(instance):
    n = instance["n"]

    pool = IDPool()
    # x[p] = the card at position p of the circle (positions 0..n-1)
    x = [Integer(f"x{p}", 1, n, vpool=pool) for p in range(n)]
    engine = IntegerEngine(vars=x, vpool=pool)

    # every card appears once
    engine.add_alldifferent(x)
    # the frog starts on card 1, which lies at position 0
    engine.add_linear(x[0] == 1)
    cnf = engine.clausify()

    # at_step[i][p] is true when the frog is at position p after i jumps
    at_step = [[pool.id(("at", i, p)) for p in range(n)] for i in range(n)]

    # the frog is on position 0 before it jumps, and on exactly one position after each jump
    cnf.append([at_step[0][0]])
    for i in range(n):
        cnf.extend(CardEnc.equals(lits=at_step[i], bound=1, vpool=pool, encoding=EncType.seqcounter).clauses)

    # a jump moves the frog from position p, where card v lies, to position (p + v) mod n
    for i in range(1, n):
        for p in range(n):
            for v in range(1, n + 1):
                cnf.append([-at_step[i - 1][p], -x[p].equals(v), at_step[i][(p + v) % n]])

    # the frog visits every position once: the positions after the n steps are all different
    for p in range(n):
        cnf.extend(CardEnc.equals(lits=[at_step[i][p] for i in range(n)], bound=1, vpool=pool,
                                  encoding=EncType.seqcounter).clauses)

    return cnf, {"x": x}
