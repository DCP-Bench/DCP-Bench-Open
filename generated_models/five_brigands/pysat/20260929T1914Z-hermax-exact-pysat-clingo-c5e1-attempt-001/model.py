# Five brigands: Alfonso, Benito, Carlos, Diego and Esteban share 200 doubloons,
# each has at least one, and the total would still be 200 if Alfonso had twelve
# times as much, Benito three times, Carlos the same, Diego half and Esteban a third.
from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine

# 12A + 3B + C + D/2 + E/3 = 200, multiplied by 6 to get whole numbers
TIMES_SIX = {"A": 72, "B": 18, "C": 6, "D": 3, "E": 2}


def build(instance):
    # The puzzle is fixed by the problem; the instance carries no data.
    pool = IDPool()
    # A share is at least 1. In the second condition the others take at least their
    # coefficient each, which caps a share at (1200 - the others) / its coefficient.
    total_coefficients = sum(TIMES_SIX.values())
    share = {name: Integer(name, 1, min(200, (1200 - (total_coefficients - c)) // c), vpool=pool)
             for name, c in TIMES_SIX.items()}
    engine = IntegerEngine(vars=list(share.values()), vpool=pool)

    # together they have 200 doubloons
    engine.add_linear(sum(share[name] for name in TIMES_SIX) == 200)
    # with the changed amounts they would still have 200 (times 6)
    engine.add_linear(sum(c * share[name] for name, c in TIMES_SIX.items()) == 1200)

    return engine.clausify(), share
