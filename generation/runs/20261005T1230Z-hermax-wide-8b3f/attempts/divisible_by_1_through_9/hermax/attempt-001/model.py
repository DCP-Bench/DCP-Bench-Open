# Divisible by 1 through 9: find the ten-digit number that uses each digit 0-9 exactly once and
# where the number formed by its first n digits is divisible by n, for n = 1..10.
from hermax.model import Model


def build(instance):
    # The number has ten digits, each 0..9 (given by the problem; the instance has no fields).
    n_digits = 10

    m = Model()
    # digit[i] = the i-th digit of the number, read from the left
    digit = m.int_vector("digit", n_digits, 0, 9)

    # each of the digits 0 to 9 is used exactly once
    m &= digit.all_different()

    # the number formed by the first k digits, digit[0] ... digit[k-1], is divisible by k.
    # That number is sum(digit[j] * 10**(k-1-j)), and only its remainder modulo k matters, so
    # each place value is replaced by its remainder modulo k. The coefficients then stay below k
    # instead of reaching 10**9, and the constraint reads sum(c[j] * digit[j]) == k * q for an
    # integer q bounded by the largest value the reduced sum can take. hermax has no `%` on an
    # IntVar, which is why divisibility is written as a product with a quotient.
    for k in range(1, n_digits + 1):
        terms = [(pow(10, k - 1 - j, k), digit[j]) for j in range(k)]
        terms = [(c, d) for c, d in terms if c != 0]
        if not terms:
            continue  # every place value is a multiple of k (always so for k = 1)
        q = m.int(f"quotient_{k}", 0, sum(c * 9 for c, _ in terms) // k)
        m &= (sum(c * d for c, d in terms) == k * q)

    # number = the whole ten-digit number. One IntVar over 0..10**10 does not fit in memory, so
    # the output is the sum of the digits times their place values.
    number = sum(10 ** (n_digits - 1 - i) * digit[i] for i in range(n_digits))

    return m, {"number": number}
