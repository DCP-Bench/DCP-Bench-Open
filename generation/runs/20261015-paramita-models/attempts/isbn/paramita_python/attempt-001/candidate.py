from paramita.modelling import Bool

# ISBN-13 validation and check digit calculation.
# Each of the 13 digits is one-hot over 0..9. Given digits are fixed by a unit constraint.

DIGITS = range(10)


def build(instance):
    given = instance["isbn_init"]
    n = len(given)

    # one-hot encoding of each digit position
    x = [{v: Bool(f"d_{i}_{v}") for v in DIGITS} for i in range(n)]

    cons = []

    # each position holds exactly one digit 0..9
    for i in range(n):
        cons.append(sum(x[i].values()) == 1)

    # the given digits of the ISBN are fixed
    # (-1 marks an unknown digit, so no constraint is added for it)
    for i, g in enumerate(given):
        if g >= 0:
            cons.append(x[i][g] == 1)

    value = [sum(v * x[i][v] for v in DIGITS) for i in range(n)]

    # the number starts with 978 or 979
    # (digit 0 is 9, digit 1 is 7, digit 2 is 8 or 9)
    cons.append(x[0][9] == 1)
    cons.append(x[1][7] == 1)
    cons.append(x[2][8] + x[2][9] == 1)

    # check digit: multiply the first 12 digits alternately by 1 and 3 (starting with 1),
    # then sum the products
    weighted = sum((1 if i % 2 == 0 else 3) * value[i] for i in range(n - 1))

    # check digit = (10 - (sum % 10)) % 10, so weighted + check digit is a multiple of 10
    # (the check digit is a digit 0..9, so it is determined by the sum modulo 10)
    max_sum = sum((1 if i % 2 == 0 else 3) * 9 for i in range(n - 1)) + 9
    qs = {q: Bool(f"q_{q}") for q in range(1, max_sum // 10 + 1)}
    # exactly one multiple of 10 is taken
    cons.append(sum(qs.values()) == 1)
    cons.append(weighted + value[n - 1] == sum(10 * q * qs[q] for q in qs))

    outputs = {"isbn": value}
    return cons, outputs
