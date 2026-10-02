# Magic sequence: find integers x[0..n-1], each between 0 and n-1, such that for
# every i the number i occurs exactly x[i] times in the sequence.
from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def build(instance):
    n = instance["n"]  # length of the sequence; values and positions both run over 0..n-1

    pool = IDPool()
    # x[i] = the i-th number of the sequence (an integer between 0 and n-1)
    x = [Integer(f"x{i}", 0, n - 1, vpool=pool) for i in range(n)]
    # occurs[i][j] = 1 when the j-th number of the sequence is i, else 0
    occurs = [[Integer(f"occurs{i}_{j}", 0, 1, vpool=pool) for j in range(n)] for i in range(n)]
    engine = IntegerEngine(vars=x + [flag for row in occurs for flag in row], vpool=pool)

    # the number i occurs exactly x[i] times: the flags of i add up to x[i]
    for i in range(n):
        engine.add_linear(sum(occurs[i]) - x[i] == 0)
    cnf = engine.clausify()

    # tie each flag to the sequence: occurs[i][j] is 1 exactly when x[j] takes the value i
    for i in range(n):
        for j in range(n):
            cnf.append([-x[j].equals(i), occurs[i][j].equals(1)])
            cnf.append([x[j].equals(i), -occurs[i][j].equals(1)])

    return cnf, {"x": x}
