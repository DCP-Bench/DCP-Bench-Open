# Just forgotten: Joe's account number uses each digit 0 to n-1 once. In each of
# several tried sets exactly some given number of digits are in the right place.
from pysat.card import CardEnc, EncType
from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def build(instance):
    sets = instance["sets"]  # the digit sequences Joe tried
    num_correct = instance["num_correct_digits"]  # digits in the right place in each set
    n = len(sets[0])

    pool = IDPool()
    # x[i] = the digit at position i of the account number
    x = [Integer(f"x_{i}", 0, n - 1, vpool=pool) for i in range(n)]
    engine = IntegerEngine(vars=x, vpool=pool)
    # each digit is used exactly once
    engine.add_alldifferent(x)
    cnf = engine.clausify()

    # every tried set has exactly num_correct digits in the position they have in the number
    for tried in sets:
        cnf.extend(CardEnc.equals(lits=[x[i].equals(tried[i]) for i in range(n)], bound=num_correct,
                                  vpool=pool, encoding=EncType.seqcounter).clauses)

    return cnf, {"x": x}
