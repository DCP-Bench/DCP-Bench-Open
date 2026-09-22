# Exactly m of the n variables take a value from v.
from pysat.card import CardEnc, EncType
from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def build(instance):
    n = instance["n"]
    wanted = instance["m"]
    values = instance["v"]

    pool = IDPool()
    # 0..7 is the domain the problem statement fixes, not an instance field.
    x = [Integer(f"x{i}", 0, 7, vpool=pool) for i in range(n)]
    engine = IntegerEngine(vars=x, vpool=pool)
    cnf = engine.clausify()

    # One value literal per (variable, wanted value); exactly one value holds
    # per variable, so counting these counts the variables that hit v.
    hits = [x[i].equals(value) for i in range(n) for value in values
            if 0 <= value <= 7]
    cnf.extend(CardEnc.equals(lits=hits, bound=wanted, vpool=pool,
                              encoding=EncType.seqcounter).clauses)
    return cnf, {"x": x}
