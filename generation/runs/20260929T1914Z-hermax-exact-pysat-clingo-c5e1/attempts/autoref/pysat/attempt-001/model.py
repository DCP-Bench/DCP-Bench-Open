# Autoref: find a series s[0..n+1] in which every i from 0 to n occurs exactly
# s[i] times, and whose last element s[n+1] equals m.
from pysat.card import CardEnc, EncType
from pysat.formula import CNF, IDPool
from pysat.integer import Integer, IntegerEngine


def build(instance):
    n = instance["n"]
    last_value = instance["m"]  # required value of the last element
    length = n + 2  # the series has n + 2 positions

    pool = IDPool()
    # every value lies between 0 and n; the direct encoding has one literal per value
    s = [Integer(f"s_{k}", 0, n, vpool=pool) for k in range(length)]
    engine = IntegerEngine(vars=s, vpool=pool)
    cnf = engine.clausify()

    # the last element is m
    cnf.append([s[n + 1].equals(last_value)])

    # The value i occurs exactly s[i] times. PySAT counts against a constant, so
    # for every possible count c the counting clauses are gated by the literal
    # "s[i] == c": each clause carries the extra literal -(s[i] == c) and only
    # binds when s[i] takes that value.
    for i in range(n + 1):
        holds_i = [s[k].equals(i) for k in range(length)]
        for count in range(n + 1):
            gate = -s[i].equals(count)
            counting = CardEnc.equals(lits=holds_i, bound=count, vpool=pool, encoding=EncType.seqcounter)
            for clause in counting.clauses:
                cnf.append([gate] + clause)

    return cnf, {"s": s}
