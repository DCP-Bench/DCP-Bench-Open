# Find a 10 digit number that uses each of the digits 0 to 9 exactly once and where
# the number formed by the first n digits of the number is divisible by n (n = 1..10).
# Digits are one-hot: y[p][v] is true when digit position p (1 = leftmost) holds digit v.
from paramita.modelling import Bool

N_DIGITS = 10


def build(instance):
    cons = []
    y = [[Bool(f"d_{p}_{v}") for v in range(10)] for p in range(1, N_DIGITS + 1)]

    # the number has 10 digits: every position holds exactly one digit
    for p in range(N_DIGITS):
        cons.append(sum(y[p]) == 1)

    # a 10 digit number has a nonzero leading digit
    cons.append(~y[0][0])

    # the number uses each of the digits 0 to 9 exactly once
    for v in range(10):
        cons.append(sum(y[p][v] for p in range(N_DIGITS)) == 1)

    # the number formed by the first k digits is divisible by k, for k = 1..10
    # (k = 1 holds for every digit, so it is left out)
    # Prefix P_k = sum_p 10^(k-p) * d_p. Replacing each power by 10^(k-p) mod k keeps
    # P_k mod k, so P_k is divisible by k exactly when sum_p c_p * d_p = k * t for some t.
    # The weights stay below 9 * 9 * k, so the sum is small.
    for k in range(2, N_DIGITS + 1):
        coeffs = [pow(10, k - p, k) for p in range(1, k + 1)]
        # the weighted digit sum of the first k digits
        weighted = sum(c * v * y[p - 1][v]
                       for p in range(1, k + 1) if coeffs[p - 1] != 0
                       for v in range(10) for c in [coeffs[p - 1]])
        max_sum = 9 * sum(coeffs)
        t_max = max_sum // k
        # quotient t, one-hot over 0..t_max
        t = [Bool(f"t_{k}_{m}") for m in range(t_max + 1)]
        cons.append(sum(t) == 1)
        # the first k digits form a number divisible by k
        cons.append(weighted == k * sum(m * t[m] for m in range(t_max + 1)))

    # the number, read from its ten digits
    digit = [sum(v * y[p][v] for v in range(10)) for p in range(N_DIGITS)]
    number = sum(10 ** (N_DIGITS - 1 - p) * digit[p] for p in range(N_DIGITS))

    return cons, {"number": number}
