# Divisible by 1 through 9: find the 10-digit number that uses each digit 0..9 exactly once and
# where the number formed by its first n digits is divisible by n, for n = 1..10.
from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def build(instance):
    # The number has 10 digits, each 0..9 (given by the problem; the instance has no fields).
    n_digits = 10

    pool = IDPool()
    # x[i] = the i-th digit of the number, read from the left. Direct encoding: ten values each.
    x = [Integer(f"x{i}", 0, 9, vpool=pool) for i in range(n_digits)]
    engine = IntegerEngine(vars=x, vpool=pool)

    # each of the digits 0..9 is used exactly once
    engine.add_alldifferent(x)

    # the number formed by the first k digits, x[0] x[1] ... x[k-1], is divisible by k.
    # That number is sum(x[j] * 10**(k-1-j)), and only its remainder modulo k matters, so each
    # place value is replaced by its remainder modulo k. This keeps the coefficients below k
    # instead of up to 10**9, and the constraint says sum(c[j] * x[j]) == k * q for some integer
    # q, whose bound is the largest value that reduced sum can take.
    for k in range(1, n_digits + 1):
        coefficients = [pow(10, k - 1 - j, k) for j in range(k)]
        terms = [(c, x[j]) for j, c in enumerate(coefficients) if c != 0]
        if not terms:
            continue  # every place value is a multiple of k (always the case for k = 1)
        reduced = sum(c * digit for c, digit in terms)
        q = Integer(f"q{k}", 0, sum(c * 9 for c, _ in terms) // k, vpool=pool)
        engine.add_var(q)
        engine.add_linear(reduced - k * q == 0)

    # number = the whole 10-digit number. It can be up to 10**10, too wide for one Integer, so it
    # is declared as the sum of the digits times their place values.
    number = sum(10 ** (n_digits - 1 - i) * x[i] for i in range(n_digits))

    return engine.clausify(), {"number": number}
