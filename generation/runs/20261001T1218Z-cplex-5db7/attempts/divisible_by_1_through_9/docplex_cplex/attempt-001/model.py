"""Divisible by 1 through 10: find a ten-digit number using each digit 0..9 once, such that
the number formed by its first n digits is divisible by n, for n = 1..10.
"""
from docplex.mp.model import Model


def build(instance):
    # The problem has no instance data: ten positions and the digits 0..9.
    n = 10
    positions = range(n)
    digits = range(10)

    model = Model("divisible_by_1_through_9")

    # is_digit[i, d] is 1 when position i (from the left) holds digit d. Each position holds
    # one digit and every digit is used exactly once.
    is_digit = {(i, d): model.binary_var(name=f"pos_{i}_is_{d}") for i in positions
                for d in digits}
    for i in positions:
        model.add_constraint(model.sum(is_digit[i, d] for d in digits) == 1)
    for d in digits:
        model.add_constraint(model.sum(is_digit[i, d] for i in positions) == 1)

    def digit(i):
        return model.sum(d * is_digit[i, d] for d in digits)

    # The number formed by the first k digits is divisible by k. That prefix is
    # sum_j digit_j * 10^(k-1-j); modulo k each power of ten can be replaced by its remainder,
    # which keeps the coefficients below k instead of up to 10^9 (CPLEX works in doubles).
    # The reduced sum is then a multiple of k: it equals k * q for an integer q >= 0.
    for k in range(1, n + 1):
        coefficients = [pow(10, k - 1 - j, k) for j in range(k)]
        reduced = model.sum(c * digit(j) for j, c in enumerate(coefficients) if c)
        top = sum(9 * c for c in coefficients) // k
        q = model.integer_var(0, top, name=f"quotient_{k}")
        model.add_constraint(reduced == k * q)

    # The ten-digit number, read from its digits. Its value is below 2^53, so the runner's
    # double arithmetic over the 0/1 values gives it exactly.
    number = model.sum(d * 10 ** (n - 1 - i) * is_digit[i, d] for i in positions
                       for d in digits if d)

    return model, {"number": number}
