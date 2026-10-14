# Five statements: statement i (counting from 1) says "exactly i of these five statements are
# false". Decide which of the statements are true.
from pysat.card import CardEnc, EncType
from pysat.formula import CNF, IDPool


def build(instance):
    n = 5  # number of statements (fixed by the puzzle)

    pool = IDPool()
    # statements[i] is true when statement i + 1 holds
    statements = [pool.id(("statement", i)) for i in range(n)]
    cnf = CNF()

    # false_count[c] says "exactly c of the statements are false". The number of false
    # statements is one particular value, so exactly one of these literals holds.
    false_count = [pool.id(("false_count", c)) for c in range(n + 1)]
    cnf.append(false_count)
    for c in range(n + 1):
        for other in range(c + 1, n + 1):
            cnf.append([-false_count[c], -false_count[other]])
        # false_count[c] may only hold when exactly c statements are false. The literal guards
        # every clause of the cardinality encoding, so the encoding is switched off otherwise.
        counting = CardEnc.equals(lits=[-s for s in statements], bound=c, vpool=pool,
                                  encoding=EncType.seqcounter)
        for clause in counting.clauses:
            cnf.append([-false_count[c]] + clause)

    # statement i + 1 is true exactly when exactly i + 1 statements are false
    for i in range(n):
        cnf.append([-statements[i], false_count[i + 1]])
        cnf.append([statements[i], -false_count[i + 1]])

    return cnf, {"statements": statements}
