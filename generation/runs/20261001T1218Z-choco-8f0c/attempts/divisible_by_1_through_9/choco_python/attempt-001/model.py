# Divisible by 1 through 10: find a 10-digit number using each digit 0-9 once such that the number
# formed by its first n digits is divisible by n, for every n.
from pychoco.model import Model

# The puzzle has no instance data; ten digits and the divisibility rule are its statement.
N_DIGITS = 10


def build(instance):
    del instance  # the puzzle carries no instance data

    model = Model()

    # x[i] = the i-th digit, read left to right
    x = [model.intvar(0, 9, name=f"x_{i}") for i in range(N_DIGITS)]
    # t[i] = the number formed by the first i+1 digits. The full number has ten digits, which is
    # beyond Choco's 32-bit integer domain; it is declared here with that bound regardless.
    t = [model.intvar(0, 10 ** (i + 1) - 1, name=f"t_{i}", bounded_domain=True)
         for i in range(N_DIGITS)]

    # Each digit 0-9 is used exactly once.
    model.all_different(x).post()

    for i in range(N_DIGITS):
        # t[i] is the number spelt by the first i+1 digits.
        model.scalar(x[:i + 1], [10 ** (i - j) for j in range(i + 1)], "=", t[i]).post()
        # It is divisible by i+1: t[i] = (i+1) * q for a whole q.
        q = model.intvar(0, (10 ** (i + 1) - 1) // (i + 1), name=f"q_{i}", bounded_domain=True)
        model.scalar([t[i], q], [1, -(i + 1)], "=", 0).post()

    return model, {"number": t[N_DIGITS - 1]}
